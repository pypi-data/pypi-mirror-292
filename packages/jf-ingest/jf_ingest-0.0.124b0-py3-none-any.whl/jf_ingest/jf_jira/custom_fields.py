import ast
import dataclasses
import functools
import json
import logging
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, NamedTuple, Optional

import requests
from opentelemetry import baggage, context, trace

from jf_ingest import logging_helper
from jf_ingest.config import IngestionConfig
from jf_ingest.jf_jira import (
    get_jira_connection,
    get_jira_search_batch_size,
    pull_jira_issues_by_jira_ids,
)
from jf_ingest.telemetry.tracing import jelly_trace, record_span
from jf_ingest.utils import ThreadPoolExecutorWithLogging, retry_for_status

JELLYFISH_CUSTOM_FIELDS_API_LIMIT = 10_000
JELLYFISH_API_TIMEOUT = 600.0


@dataclasses.dataclass
class JCFVDBData:
    field_id: int
    field_key: str
    field_type: str
    value: str


@dataclasses.dataclass
class IssueJCFVDBData:
    issue_jira_id: int
    custom_field_values: list[JCFVDBData]


@dataclasses.dataclass
class JCFVUpdate:
    jira_issue_id: int
    field_id: int
    field_key: str
    field_type: str
    value_old: Optional[str]
    value_new: Optional[str]


@functools.lru_cache(maxsize=16384)
def _literal_eval_memoized(value: str) -> dict:
    """ast.literal_eval is rather slow, and we expect a lot of duplicate values; memoize it."""
    return ast.literal_eval(value)


@functools.lru_cache(maxsize=16384)
def _json_loads_memoized(value: str) -> dict:
    """improve performance of JSON loads by memoizing the results."""
    return json.loads(value)


@jelly_trace
def _annotate_results_from_jellyfish(data: dict) -> dict[str, IssueJCFVDBData]:
    """
    Unpacks the results from Jellyfish into a dict[str, IssueJCFVDBData] - where `str` is the jira_issue_id.

    Typically, the value being sent over is JSON, so we need to handle that here.
    """
    resp = {}
    for issue in data['issues']:
        resp[str(issue['issue_jira_id'])] = IssueJCFVDBData(
            issue_jira_id=issue['issue_jira_id'], custom_field_values=[]
        )
        for jcfv_db_data in issue['custom_field_values']:
            value = jcfv_db_data['value']
            if value and isinstance(value, str):
                try:
                    value = _json_loads_memoized(value)
                except (json.JSONDecodeError, ValueError):
                    try:
                        value = _literal_eval_memoized(value)
                    except ValueError:
                        pass
            resp[str(issue['issue_jira_id'])].custom_field_values.append(
                JCFVDBData(
                    field_id=jcfv_db_data['field_id'],
                    field_key=jcfv_db_data['field_key'],
                    field_type=jcfv_db_data['field_type'],
                    value=value,
                )
            )
    return resp


@jelly_trace
def _retrieve_custom_fields_from_jellyfish(
    ingest_config: IngestionConfig,
    output_queue: queue.Queue,
    max_issues_to_process: Optional[int] = None,
    limit: int = JELLYFISH_CUSTOM_FIELDS_API_LIMIT,
) -> None:
    """
    Retrieve all custom fields from Jellyfish. Returns dict[str, IssueJCFVDBData] -
    where `str` is the jira_issue_id - to the output queue. Should be spawned in a separate thread.

    Note: 10K is the API hard limit.
    """
    if max_issues_to_process == 0:
        return

    offset = 0
    limit = min((limit, max_issues_to_process)) if max_issues_to_process else limit

    while True:
        base_url = ingest_config.jellyfish_api_base
        headers = {"Jellyfish-API-Token": ingest_config.jellyfish_api_token}
        st = time.perf_counter()

        def _get_values_from_jellyfish() -> requests.Response:
            """define this as a function, so we can use with retry_for_status"""
            response = requests.get(
                f"{base_url}/endpoints/jira/issues/custom-fields?offset={offset}&limit={limit}",
                headers=headers,
                timeout=JELLYFISH_API_TIMEOUT,
            )
            try:
                response.raise_for_status()
            except Exception as e:
                logging_helper.send_to_agent_log_file(
                    f'Error when attempting to pull custom fields from Jellyfish: {e}'
                )
                raise e
            return response

        # Sometimes we'll see 504's from Jellyfish (e.g. if pulling a large amount of data)
        # so we'll retry for status here.
        r = retry_for_status(_get_values_from_jellyfish)

        data = r.json()
        if not data['issues']:
            logging_helper.send_to_agent_log_file(
                f'No more issues found when attempting to pull custom fields from Jellyfish. {offset} issues retrieved.',
            )
            break

        # API is hard-limited to 10K, which we should be respecting
        # here, but let's do this just-in-case.
        limit = min((limit, data['max_records']))
        # Handle the case where we have a max_issues_to_process, that
        # isn't a clean multiple of limit
        limit = min((limit, max_issues_to_process - offset)) if max_issues_to_process else limit
        offset += data['total_records']

        # Annotate data to be put into the output queue.
        output_queue.put(_annotate_results_from_jellyfish(data))

        if max_issues_to_process is not None and offset >= max_issues_to_process:
            logging_helper.send_to_agent_log_file(
                f'Finished pulling custom fields from Jellyfish - reached max_issues_to_process. {offset} issues retrieved.'
            )
            break
        if data['total_records'] < limit:
            logging_helper.send_to_agent_log_file(
                f'Finished pulling custom fields from Jellyfish - reached end of data. {offset} issues retrieved.'
            )
            break
        logging_helper.send_to_agent_log_file(
            f'Pulled {offset} issues from Jellyfish, {len(data["issues"])} records in {time.perf_counter() - st:.2f}s,'
            f' continuing...'
        )


class JCFVUpdateFullPayload(NamedTuple):
    missing_from_db_jcfv: list[JCFVUpdate]
    missing_from_jira_jcfv: list[JCFVUpdate]
    out_of_sync_jcfv: list[JCFVUpdate]


@jelly_trace
def identify_custom_field_mismatches(
    ingest_config: IngestionConfig,
    nthreads: int = 10,
    max_issues_to_process: Optional[int] = None,
) -> JCFVUpdateFullPayload:
    """
    At a high level:
    - Get all of the fields that are used to define critical components in Jellyfish. We use a Jellyfish
        endpoint to get this data, in order to support using this sync path from both the agent and internally.
    - Create one thread that retrieves (issue.id, issue.jira_id, *custom_field_values) of all issues
        and puts that into a queue. This is done in a separate thread to allow us to download issues from Jira
        in parallel, as downloading issues from Jira is the primary bottleneck.
    - In our main thread, read from the queue that's being stuffed by the _retrieve_custom_fields_from_jellyfish
        thread, and query Jira to get up-to-date issue data. If there is any data mismatch in custom
        fields, save that into an "updates" NamedTuple, which we can POST to Jellyfish to update the data.

    :param ingest_config: IngestionConfig object
    :param nthreads: Number of threads to use for downloading issues from Jira
    :param max_issues_to_process: Maximum number of issues to process. If None, all issues will be processed.
    :return: Tuple of (missing_from_db_jcfv, missing_from_jira_jcfv, out_of_sync_jcfv)
    """
    output_queue = queue.Queue()

    # Use ThreadPoolExecutor here so that we can capture
    # any exceptions raised within the thread.
    executor = ThreadPoolExecutorWithLogging(max_workers=1)
    retrieval_thread = executor.submit(
        _retrieve_custom_fields_from_jellyfish,
        ingest_config,
        output_queue,
        max_issues_to_process=max_issues_to_process,
    )

    # We _are_ downloading issues but not doing a full download, so for_download=False
    # is fine here and is faster.
    jira_connection = get_jira_connection(config=ingest_config.jira_config)

    # We store the custom field values that are missing from the DB, missing from Jira,
    # and out of sync in separate lists - this allows for easier processing on the
    # update side.
    update_payload = JCFVUpdateFullPayload([], [], [])

    st = time.perf_counter()
    total_issues_scanned = 0
    while retrieval_thread.running() or not output_queue.empty():
        try:
            db_issue_batch: dict[str, IssueJCFVDBData] = output_queue.get(timeout=60.0)
        except queue.Empty:
            logging_helper.send_to_agent_log_file(
                'Didn\'t get any issues from the queue in 60 seconds, retrying...'
            )
            continue

        total_issues_scanned += len(db_issue_batch)

        # Get all the field keys from the DB data, so we can request them from Jira.
        field_map = {}
        for issue in db_issue_batch.values():
            for jcfv in issue.custom_field_values:
                field_map[jcfv.field_key] = (jcfv.field_id, jcfv.field_key, jcfv.field_type)

        # If we don't have any fields to query, we can skip the Jira query.
        if not field_map:
            continue

        # Likely won't change the batch size vs. doing this without "fields", but
        # it's possible we'll be able to use a larger batch size if querying a subset
        # of fields.
        batch_size = get_jira_search_batch_size(
            jira_connection, fields=['key'] + list(field_map.keys())
        )

        # Note: this is parallelized and returns a generator, so we're
        # able to process issues while downloading from Jira simultaneously.
        with record_span('jira_issues_download'):
            jira_issue_batch = pull_jira_issues_by_jira_ids(
                jira_connection=jira_connection,
                jira_ids=list(db_issue_batch.keys()),
                num_parallel_threads=nthreads,
                batch_size=batch_size,
                include_fields=['key'] + list(field_map.keys()),
            )

        # Now we need to compare the custom field values from the DB with the actual issue data from Jira.
        tracer = trace.get_tracer(__name__)
        compare_issues_to_db_span = tracer.start_span(name='compare_issues_to_db')
        for issue_jira in jira_issue_batch:
            issue_db = db_issue_batch[str(issue_jira['id'])]
            jcfv_db_dict = {jcfv.field_key: jcfv for jcfv in issue_db.custom_field_values}

            for field_id, field_key, field_type in field_map.values():
                # Attempt to get the custom field value from the DB.
                # This may not be present, in the case that the field was
                # added to the issue, but we haven't yet pulled the data.
                db_value = getattr(jcfv_db_dict.get(field_key), 'value', None)

                # Occasionally, an issue may not have any of the fields we
                # requested, (e.g. if we're looking for just one field which is
                # no longer present on the issue present) so we need to handle this case.
                jira_value = issue_jira.get('fields', {}).get(field_key, None)

                if db_value != jira_value:
                    if db_value is None:
                        list_to_append = update_payload.missing_from_db_jcfv
                    elif jira_value is None:
                        list_to_append = update_payload.missing_from_jira_jcfv
                    else:
                        list_to_append = update_payload.out_of_sync_jcfv
                    list_to_append.append(
                        JCFVUpdate(
                            field_id=field_id,
                            field_key=field_key,
                            field_type=field_type,
                            jira_issue_id=issue_db.issue_jira_id,
                            value_old=db_value,
                            value_new=jira_value,
                        )
                    )
        compare_issues_to_db_span.end()

        total_fields_out_of_sync = sum(map(len, update_payload))
        logging_helper.send_to_agent_log_file(
            f'Downloaded {total_issues_scanned} issues from Jira. '
            f'{total_fields_out_of_sync} out of sync field values found '
            f'so far in {time.perf_counter() - st} seconds.'
        )
        st = time.perf_counter()

    # Run here in case we get no issues back from Jellyfish
    total_fields_out_of_sync = sum(map(len, update_payload))
    logging_helper.send_to_agent_log_file(
        f'Finished processing all issues from the DB. {total_fields_out_of_sync} '
        f'out of sync field values found in total.'
    )
    logging_helper.send_to_agent_log_file(
        f'{len(update_payload.out_of_sync_jcfv)} custom field values to update.'
    )
    logging_helper.send_to_agent_log_file(
        f'{len(update_payload.missing_from_jira_jcfv)} custom field values to delete.'
    )
    logging_helper.send_to_agent_log_file(
        f'{len(update_payload.missing_from_db_jcfv)} custom field values to insert.'
    )
    logging_helper.send_to_agent_log_file(f'{total_issues_scanned} issues scanned in total.')

    # Retrieval thread is already finished, as guaranteed by the while loop above.
    # We can safely call result() here, which will raise any exceptions we might have seen.
    retrieval_thread.result()

    return update_payload
