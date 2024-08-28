from pantomath_sdk import JobRun
from pantomath_sdk import AstroDag
from pantomath_sdk import PantomathApiClient
from pantomath_sdk import JobRunLogStatuses
from pantomath_sdk import DataikuDataset
import requests_mock

goodApiClient = PantomathApiClient(api_key="1234")
good_job = AstroDag(name="TestJob", host_name="testHost")

mock_data_set = DataikuDataset(
    host_name="host_name",
    project_key="project_key",
    dataset_name="dataset_name",
)
good_job_run_log = {
    "job": good_job,
    "name": "TestJobRunLog",
    "source_data_sets": [mock_data_set],
    "target_data_sets": [mock_data_set],
    "next_run_at": "next_run_at",
    "pantomath_api_client": goodApiClient,
}


def test_PostJobRunLog_get_functions():
    post_job_run_log = JobRun(**good_job_run_log)
    assert (
        post_job_run_log._get_normalized_message("Hello")
        == "TestJobRunLog running in TestJob: Hello"
    )
    post_job = post_job_run_log.get_job()
    assert post_job == good_job
    testDataSet = post_job_run_log.get_source_data_sets()
    assert testDataSet[0] == {
        "objectName": mock_data_set.get_name(),
        "objectType": mock_data_set.get_type(),
        "fullyQualifiedObjectName": mock_data_set.get_fully_qualified_object_name(),
    }
    testDataSet = post_job_run_log.get_target_data_sets()
    assert testDataSet[0] == {
        "objectName": mock_data_set.get_name(),
        "objectType": mock_data_set.get_type(),
        "fullyQualifiedObjectName": mock_data_set.get_fully_qualified_object_name(),
    }
    assert post_job_run_log.get_next_run_at() == "next_run_at"


def test_PostJobRunLog_log_start_without_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_start(records_effected=42)
        assert len(post_job_run_log._log_buffer) == 0
        assert mock.last_request.json().get("jobRunLogs")[0]["recordsEffected"] == 42
        assert (
            mock.last_request.json().get("jobRunLogs")[0]["status"]
            == JobRunLogStatuses.STARTED.value
        )
        assert (
            mock.last_request.json().get("jobRunLogs")[0]["message"]
            == "TestJobRunLog running in TestJob: Started"
        )
        assert mock.call_count == 1


def test_PostJobRunLog_log_start_with_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_start(records_effected=42, message="Test")
        assert len(post_job_run_log._log_buffer) == 0
        assert mock.last_request.json().get("jobRunLogs")[0]["recordsEffected"] == 42
        assert (
            mock.last_request.json().get("jobRunLogs")[0]["status"]
            == JobRunLogStatuses.STARTED.value
        )
        assert (
            mock.last_request.json().get("jobRunLogs")[0]["message"]
            == "TestJobRunLog running in TestJob: Test"
        )
        assert mock.call_count == 1


def test_PostJobRunLog_log_progress_without_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_progress(records_effected=42)
        assert len(post_job_run_log._log_buffer) == 1
        assert post_job_run_log._log_buffer[0]["recordsEffected"] == 42
        assert (
            post_job_run_log._log_buffer[0]["status"]
            == JobRunLogStatuses.IN_PROGRESS.value
        )
        assert (
            post_job_run_log._log_buffer[0]["message"]
            == "TestJobRunLog running in TestJob: Progressing"
        )
        assert mock.call_count == 0


def test_PostJobRunLog_log_progress_with_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_progress(records_effected=42, message="Test")
        assert len(post_job_run_log._log_buffer) == 1
        assert post_job_run_log._log_buffer[0]["recordsEffected"] == 42
        assert (
            post_job_run_log._log_buffer[0]["status"]
            == JobRunLogStatuses.IN_PROGRESS.value
        )
        assert (
            post_job_run_log._log_buffer[0]["message"]
            == "TestJobRunLog running in TestJob: Test"
        )
        assert mock.call_count == 0


def test_PostJobRunLog_log_warning_without_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_warning(records_effected=42)
        assert len(post_job_run_log._log_buffer) == 1
        assert post_job_run_log._log_buffer[0]["recordsEffected"] == 42
        assert (
            post_job_run_log._log_buffer[0]["status"] == JobRunLogStatuses.WARNING.value
        )
        assert (
            post_job_run_log._log_buffer[0]["message"]
            == "TestJobRunLog running in TestJob: Warning"
        )
        assert mock.call_count == 0


def test_PostJobRunLog_log_warning_with_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_warning(records_effected=42, message="Test")
        assert len(post_job_run_log._log_buffer) == 1
        assert post_job_run_log._log_buffer[0]["recordsEffected"] == 42
        assert (
            post_job_run_log._log_buffer[0]["status"] == JobRunLogStatuses.WARNING.value
        )
        assert (
            post_job_run_log._log_buffer[0]["message"]
            == "TestJobRunLog running in TestJob: Test"
        )
        assert mock.call_count == 0


def test_PostJobRunLog_log_success_without_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_success(records_effected=42)
        assert len(post_job_run_log._log_buffer) == 0
        assert mock.call_count == 1


def test_PostJobRunLog_log_success_with_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_success(records_effected=42, message="Test")
        assert len(post_job_run_log._log_buffer) == 0
        assert mock.call_count == 1


def test_PostJobRunLog_log_failed_without_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_failure(records_effected=42)
        assert len(post_job_run_log._log_buffer) == 0
        assert mock.call_count == 1


def test_PostJobRunLog_log_failed_with_message():
    with requests_mock.Mocker() as mock:
        mock.post("https://api.dev-pantomath.org/v1/job-run-logs", status_code=200)
        post_job_run_log = JobRun(**good_job_run_log)
        post_job_run_log.log_failure(records_effected=42, message="Test")
        assert len(post_job_run_log._log_buffer) == 0
        assert mock.call_count == 1
