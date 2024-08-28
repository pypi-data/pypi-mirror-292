from pantomath_sdk import JobRunLogStatuses


def test_get_job_run_log_statuses():
    expected_list = [
        "STARTED",
        "IN_PROGRESS",
        "SUCCEEDED",
        "FAILED",
        "QUEUED",
        "WARNING",
    ]
    statuses = JobRunLogStatuses.get_job_run_log_statuses()
    assert statuses.sort() == expected_list.sort()


def test_is_job_run_log_status():
    assert JobRunLogStatuses.is_job_run_log_status("SUCCEEDED")


def test_not_is_job_run_log_status():
    assert not JobRunLogStatuses.is_job_run_log_status("FOO")
