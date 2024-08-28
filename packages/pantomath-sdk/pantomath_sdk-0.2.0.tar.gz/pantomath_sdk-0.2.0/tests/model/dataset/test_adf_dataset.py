from pantomath_sdk import ADFDataset


def test_adf_dataset_good():
    test_node = ADFDataset(data_set_id="96868946864896189", name="ADF Unit Test")
    assert test_node.get_name() == "ADF Unit Test"
    assert test_node.get_type() == "ADF_DATASET"
    assert test_node.get_fully_qualified_object_name() == "96868946864896189"
