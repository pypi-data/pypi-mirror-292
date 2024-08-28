from pantomath_sdk import JobRunLog
import datetime


def test_job_run_log_get_functions():
    mock_data = {
        "job_run": "job_run",
        "status": "status",
        "message": "message",
        "records_effected": 42,
        "timestamp": datetime.datetime(2024, 7, 17, 19, 28, 26, 566012),
    }
    post_job_run_log = JobRunLog(**mock_data)
    assert post_job_run_log.get_unique_id() is not None
    assert post_job_run_log.get_job_run() == mock_data["job_run"]
    assert post_job_run_log.get_status() == mock_data["status"]
    assert post_job_run_log.get_message() == mock_data["message"]
    assert post_job_run_log.get_records_effected() == mock_data["records_effected"]
    assert post_job_run_log.get_timestamp() == "2024-07-17T19:28:26.566012Z"


def test_job_run_log_get_functions_no_optional_params():
    mock_data = {
        "job_run": "job_run",
        "status": "status",
        "timestamp": datetime.datetime(2024, 7, 17, 19, 28, 26, 566012),
    }
    post_job_run_log = JobRunLog(**mock_data)
    assert post_job_run_log.get_unique_id() is not None
    assert post_job_run_log.get_job_run() == mock_data["job_run"]
    assert post_job_run_log.get_status() == mock_data["status"]
    assert post_job_run_log.get_message() is None
    assert post_job_run_log.get_records_effected() is None
    assert post_job_run_log.get_timestamp() == "2024-07-17T19:28:26.566012Z"
