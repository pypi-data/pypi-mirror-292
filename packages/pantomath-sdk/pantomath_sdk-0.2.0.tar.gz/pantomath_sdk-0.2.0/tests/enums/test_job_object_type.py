from pantomath_sdk import JobObjectTypes


def test_get_job_object_types():
    expected_list = [
        "SQL_FUNCTION",
        "SQL_PROCEDURE",
        "TABLEAU_EXTRACT_REFRESH_TASK",
        "FIVETRAN_CONNECTOR",
        "DBT_MODEL",
        "POWER_BI_REFRESH",
        "POWER_BI_ACTIVITY",
        "POWER_BI_DATAFLOW",
        "ADF_ACTIVITY",
        "ADF_PIPELINE",
        "JOB",
        "ACTIVITY",
        "DATAFLOW",
        "PIPELINE",
        "PACKAGE",
        "COMPONENT",
        "REFRESH",
        "TASK",
        "SNOWFLAKE_PIPE",
    ]
    statuses = JobObjectTypes.get_job_object_types()
    assert statuses.sort() == expected_list.sort()


def test_is_job_object_type():
    assert JobObjectTypes.is_job_object_type("POWER_BI_DATAFLOW")


def test_not_is_job_object_type():
    assert not JobObjectTypes.is_job_object_type("FOO")
