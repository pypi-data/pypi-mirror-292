from pantomath_sdk import DataikuDataset


def test_dataiku_dataset_good():
    test_node = DataikuDataset(
        host_name="host",
        project_key="96868946864896189",
        dataset_name="DataikuDataset Unit Test",
    )
    assert test_node.get_name() == "DataikuDataset Unit Test"
    assert test_node.get_type() == "DATASET"
    assert (
        test_node.get_fully_qualified_object_name()
        == "host/projects/96868946864896189/datasets/dataikudataset%20unit%20test"
    )
