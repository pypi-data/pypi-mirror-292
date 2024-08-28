from pantomath_sdk import PantomathApiClient
from pantomath_sdk import JobRunLogStatuses
import requests_mock
import pytest
import sys

mock_data_set = {
    "objectName": "objectName",
    "objectType": "objectType",
    "fullyQualifiedObjectName": "fullyQualifiedObjectName",
}


def assert_basic_request_data(mock, request):
    assert mock.called
    assert mock.call_count == 1
    assert request.method == "POST"
    assert "x-api-key" in request.headers
    assert "x-sdk-type" in request.headers
    assert request.headers["x-sdk-type"] == "Python"
    assert request.headers["x-api-key"] == "1234"


def test_post_job_run_logs_no_data():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client.post_job_run_logs(jobRunLogs=None)
        assert mock.call_count == 0


def test_post_job_run_logs_bad_data():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client.post_job_run_logs(jobRunLogs="test")
        assert mock.call_count == 0


def test_post_job_run_logs_good_data():
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "targetDataSets": [mock_data_set],
        "sourceDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client.post_job_run_logs(jobRunLogs=[log])
        request = mock.request_history[0]
        assert_basic_request_data(mock, request)
        sys.stdout.write(request.body)
        assert "jobRunLogs" in request.body


def test_post_job_run_logs_good_data_2():
    client = PantomathApiClient(api_key="1234")
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "targetDataSets": [mock_data_set],
        "sourceDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client.post_job_run_logs(jobRunLogs=[log, log, log])
        request = mock.request_history[0]
        assert_basic_request_data(mock, request)
        sys.stdout.write(request.body)
        assert "jobRunLogs" in request.body


def test_post_job_run_logs_one_bad_data():
    good_log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "targetDataSets": [mock_data_set],
        "sourceDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    bad_log = {}
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        with pytest.raises(TypeError):
            client.post_job_run_logs(jobRunLogs=[good_log, good_log, good_log, bad_log])
        assert mock.call_count == 0


def test_send_log_no_data():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client._send_logs(None)
        assert mock.call_count == 0


def test_send_logs_bad_data():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client._send_logs("test")
        assert mock.call_count == 1


def test_send_logs_good_data():
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "targetDataSets": [mock_data_set],
        "sourceDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        client = PantomathApiClient(api_key="1234")
        client._send_logs([log])
        request = mock.request_history[0]
        assert_basic_request_data(mock, request)
        sys.stdout.write(request.body)
        assert "jobRunLogs" in request.body


def test_send_log_data_good_data():
    client = PantomathApiClient(api_key="1234")
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "targetDataSets": [mock_data_set],
        "sourceDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    result = client.validate_log_data(log)
    assert result


def test_send_log_data_bad_tdataset():
    client = PantomathApiClient(api_key="1234")
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "targetDataSets": "BAD_DATA",
        "sourceDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    result = client.validate_log_data(log)
    assert not result


def test_send_log_data_bad_sdataset():
    client = PantomathApiClient(api_key="1234")
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "recordsEffected": 42,
        "sourceDataSets": "BAD_DATA",
        "targetDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    result = client.validate_log_data(log)
    assert not result


def test_send_log_data_no_optional():
    client = PantomathApiClient(api_key="1234")
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": JobRunLogStatuses.SUCCEEDED.value,
        "message": "message",
        "sourceDataSets": [mock_data_set],
        "targetDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    result = client.validate_log_data(log)
    assert result


def test_send_log_data_bad_optional():
    client = PantomathApiClient(api_key="1234")
    log = {
        "jobRunId": "jobRunId",
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "recordsEffected": "BAD_DATA",
        "sourceDataSets": [mock_data_set],
        "targetDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    result = client.validate_log_data(log)
    assert not result


def test_send_log_data_missing_data():
    client = PantomathApiClient(api_key="1234")
    log = {
        "objectName": "objectName",
        "objectType": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "recordsEffected": 42,
        "sourceDataSets": [mock_data_set],
        "targetDataSets": [mock_data_set],
        "isoTimestamp": "isoTimestamp",
    }
    result = client.validate_log_data(log)

    assert not result


def test_send_log_data_no_data():
    client = PantomathApiClient(api_key="1234")
    result = client.validate_log_data(None)
    assert not result
