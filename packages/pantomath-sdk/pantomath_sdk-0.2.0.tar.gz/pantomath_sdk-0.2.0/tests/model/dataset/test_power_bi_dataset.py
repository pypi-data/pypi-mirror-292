from pantomath_sdk import PowerBIDataset


def test_powerbi_dataset_good():
    test_node = PowerBIDataset(
        workspace_id=123124124,
        dashboard_id=9879789789,
        name="PowerBIDataset Unit Test",
    )
    assert test_node.get_name() == "PowerBIDataset Unit Test"
    assert test_node.get_type() == "POWER_BI_DATASET"
    assert (
        test_node.get_fully_qualified_object_name()
        == "app.powerbi.com/groups/123124124/datasets/9879789789"
    )
