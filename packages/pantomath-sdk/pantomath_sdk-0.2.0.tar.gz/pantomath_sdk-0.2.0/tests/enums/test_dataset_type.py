from pantomath_sdk import DataSetTypes

expected_list = [
    "SQL_TABLE",
    "SQL_VIEW",
    "SQL_MATERIALIZED_VIEW",
    "S3_BUCKET",
    "TABLEAU_WORKBOOK",
    "TABLEAU_DATASOURCE",
    "POWER_BI_DASHBOARD",
    "POWER_BI_REPORT",
    "POWER_BI_DATASET",
    "POWER_BI_DATAFLOW_ENTITY",
    "ADF_DATA_FLOW",
    "ADF_DATASET",
    "FTP",
]


def test_get_dataset_types():
    actual_statuses = DataSetTypes.get_dataset_types()
    assert actual_statuses.sort() == expected_list.sort()


def test_is_dataset_type():
    assert DataSetTypes.is_dataset_type("S3_BUCKET")


def test_not_is_dataset_type():
    assert not DataSetTypes.is_dataset_type("FOO")
