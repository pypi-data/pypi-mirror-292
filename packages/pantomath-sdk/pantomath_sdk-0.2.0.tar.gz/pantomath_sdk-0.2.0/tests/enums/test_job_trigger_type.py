from pantomath_sdk import JobTriggerTypes


def test_get_job_trigger_types():
    expected_list = ["SCHEDULE", "MANUAL", "UNKNOWN"]
    statuses = JobTriggerTypes.get_job_trigger_types()
    assert statuses.sort() == expected_list.sort()


def test_is_job_trigger_type():
    assert JobTriggerTypes.is_job_trigger_type("MANUAL")


def test_not_is_job_trigger_type():
    assert not JobTriggerTypes.is_job_trigger_type("FOO")
