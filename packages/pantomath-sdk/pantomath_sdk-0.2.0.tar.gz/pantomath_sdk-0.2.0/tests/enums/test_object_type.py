from pantomath_sdk import ObjectType


def test_get_object_types():
    expected_list = [
        "SQL_TABLE",
        "SQL_VIEW",
        "SQL_MATERIALIZED_VIEW",
        "SQL_FUNCTION",
        "SQL_PROCEDURE",
        "S3_BUCKET",
        "TABLEAU_EXTRACT_REFRESH_TASK",
        "TABLEAU_WORKBOOK",
        "TABLEAU_DATASOURCE",
        "SNOWFLAKE_PIPE",
        "FIVETRAN_CONNECTOR",
        "UNKNOWN",
        "DBT_MODEL",
        "POWER_BI_DASHBOARD",
        "POWER_BI_REPORT",
        "POWER_BI_DATASET",
        "POWER_BI_DATAFLOW_ENTITY",
        "POWER_BI_REFRESH",
        "POWER_BI_DATAFLOW",
        "POWER_BI_ACTIVITY",
        "ADF_ACTIVITY",
        "ADF_DATA_FLOW",
        "ADF_PIPELINE",
        "ADF_DATASET",
        "SYNAPSE_DATAFLOW",
        "PACKAGE",
        "COMPONENT",
        "JOB",
        "DATASOURCE",
        "DATASET",
        "DATAFLOW",
        "ACTIVITY",
        "PIPELINE",
        "REPORT",
        "TRIGGER",
        "REFRESH",
        "TASK",
    ]
    statuses = ObjectType.get_object_types()
    assert statuses.sort() == expected_list.sort()


def test_is_object_type():
    assert ObjectType.is_object_type("SQL_FUNCTION")


def test_not_is_object_type():
    assert not ObjectType.is_object_type("FOO")
