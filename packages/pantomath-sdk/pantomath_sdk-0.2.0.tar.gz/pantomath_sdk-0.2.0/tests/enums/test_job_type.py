from pantomath_sdk import JobTypes


def test_get_job_types():
    expected_list = [
        "DAG",
        "TASK",
        "SQL_FUNCTION",
        "SQL_PROCEDURE",
        "TABLEAU_EXTRACT_REFRESH_TASK",
        "FIVETRAN_CONNECTOR",
        "DBT_MODEL",
        "POWER_BI_REFRESH",
        "POWER_BI_DATAFLOW",
        "ADF_ACTIVITY",
        "ADF_PIPELINE",
        "JOB",
        "ACTIVITY",
        "PIPELINE",
        "PACKAGE",
        "COMPONENT",
        "TASK",
        "SNOWFLAKE_PIPE",
        "AWS_LAMBDA",
    ]
    statuses = JobTypes.get_job_types()
    assert statuses.sort() == expected_list.sort()


def test_is_job_type():
    assert JobTypes.is_job_type("PIPELINE")


def test_not_is_job_type():
    assert not JobTypes.is_job_type("FOO")
