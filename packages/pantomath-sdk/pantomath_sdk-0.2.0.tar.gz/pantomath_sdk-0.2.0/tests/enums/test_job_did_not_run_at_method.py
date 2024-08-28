from pantomath_sdk import JobDidNotRunAtMethods


def test_get_job_did_not_run_at_method():
    expected_list = ["TRIGGER_TYPE", "NEXT_RUN_AT"]
    statuses = JobDidNotRunAtMethods.get_job_did_not_run_at_method()
    assert statuses.sort() == expected_list.sort()


def test_is_job_did_not_run_at_method():
    assert JobDidNotRunAtMethods.is_job_did_not_run_at_method("NEXT_RUN_AT")


def test_not_is_job_did_not_run_at_method():
    assert not JobDidNotRunAtMethods.is_job_did_not_run_at_method("FOO")
