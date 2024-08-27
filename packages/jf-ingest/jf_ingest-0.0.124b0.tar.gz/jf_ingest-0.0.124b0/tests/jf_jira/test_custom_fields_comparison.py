import json
import os
import queue
from copy import deepcopy
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock

import jf_ingest.jf_jira.custom_fields as custom_fields
from jf_ingest.config import IngestionConfig, IngestionType, JiraDownloadConfig
from jf_ingest.utils import RetryLimitExceeded
from tests.jf_jira.utils import get_fixture_file_data

ATLASSIAN_BASE_URL = 'mock://test-co.atlassian.net/'
JELLYFISH_BASE_URL = 'mock://jellyfish.jellyfish'
JELLYFISH_CUSTOM_FIELDS_ENDPOINT = 'endpoints/jira/issues/custom-fields'


def _get_ingestion_config():
    company_slug = "test_company"
    url = ATLASSIAN_BASE_URL
    return IngestionConfig(
        company_slug=company_slug,
        jira_config=JiraDownloadConfig(
            company_slug=company_slug,
            url=url,
            personal_access_token='pat',
        ),
        git_configs=[],
        jellyfish_api_token='some_token',
        jellyfish_api_base=JELLYFISH_BASE_URL,
        ingest_type=IngestionType.DIRECT_CONNECT,
    )


def _get_jellyfish_custom_fields_default_response() -> dict:
    return json.loads(get_fixture_file_data(fixture_path='jellyfish_custom_fields.json'))


def _get_jellyfish_custom_fields_empty_response() -> dict:
    return json.loads(
        get_fixture_file_data(fixture_path='jellyfish_custom_fields_empty_response.json')
    )


def test_custom_fields_comparison_base_case():
    config = _get_ingestion_config()
    jf_response = _get_jellyfish_custom_fields_default_response()
    empty_response = _get_jellyfish_custom_fields_empty_response()

    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?offset=0&limit={custom_fields.JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
            json=jf_response,
            status_code=200,
        )

        mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?offset={len(jf_response['issues'])}&limit={custom_fields.JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
            json=empty_response,
            status_code=200,
        )

        # Mock out ThreadPoolExecutor to get a synchronous run
        def _synchronous_run(f, *args, **kwargs):
            f(*args, **kwargs)
            thread_obj = MagicMock()
            thread_obj.running = MagicMock()
            thread_obj.running.return_value = False
            return thread_obj

        synchronous_run_mock = MagicMock()
        custom_fields.ThreadPoolExecutor = MagicMock()
        custom_fields.ThreadPoolExecutor.return_value = synchronous_run_mock
        synchronous_run_mock.submit = _synchronous_run

        # Mock out Jira response
        issues = get_fixture_file_data(
            fixture_path=os.path.join('api_responses', 'issues_for_custom_fields.json')
        )
        issues_resp = json.loads(issues)['issues']
        custom_fields.pull_jira_issues_by_jira_ids = MagicMock()
        custom_fields.pull_jira_issues_by_jira_ids.return_value = issues_resp

        # Mock out Jira connection and batch size request
        custom_fields.get_jira_connection = MagicMock()
        custom_fields.get_jira_search_batch_size = MagicMock()
        custom_fields.get_jira_search_batch_size.return_value = 100

        # Generate update payload
        update_payload = custom_fields.identify_custom_field_mismatches(config, nthreads=1)

        assert len(update_payload.missing_from_jira_jcfv) == 1
        assert len(update_payload.missing_from_db_jcfv) == 1
        assert len(update_payload.out_of_sync_jcfv) == 1

        # Missing from Jira (DELETE)
        assert update_payload.missing_from_jira_jcfv[0].field_id == '201'
        assert update_payload.missing_from_jira_jcfv[0].field_key == 'customfield_301'
        assert update_payload.missing_from_jira_jcfv[0].field_type == 'team'
        assert update_payload.missing_from_jira_jcfv[0].jira_issue_id == '101'
        assert update_payload.missing_from_jira_jcfv[0].value_new is None
        assert update_payload.missing_from_jira_jcfv[0].value_old == {"name": "T2"}

        # Missing from DB (INSERT)
        assert update_payload.missing_from_db_jcfv[0].field_id == '201'
        assert update_payload.missing_from_db_jcfv[0].field_key == 'customfield_301'
        assert update_payload.missing_from_db_jcfv[0].field_type == 'team'
        assert update_payload.missing_from_db_jcfv[0].jira_issue_id == '100'
        assert update_payload.missing_from_db_jcfv[0].value_new == {
            'self': 'https://test-co.atlassian.net/rest/api/2/customFieldOption/12347',
            'value': 'NEW TEAM 10',
            'id': '12347',
        }
        assert update_payload.missing_from_db_jcfv[0].value_old is None

        # Out-of-sync (UPDATE)
        assert update_payload.out_of_sync_jcfv[0].field_id == '200'
        assert update_payload.out_of_sync_jcfv[0].field_key == 'customfield_300'
        assert update_payload.out_of_sync_jcfv[0].field_type == 'team'
        assert update_payload.out_of_sync_jcfv[0].jira_issue_id == '100'
        assert update_payload.out_of_sync_jcfv[0].value_new == {
            'self': 'https://test-co.atlassian.net/rest/api/2/customFieldOption/12345',
            'value': 'NEW TEAM 1',
            'id': '12345',
        }
        assert update_payload.out_of_sync_jcfv[0].value_old == {"name": "T1"}
