from pantomath_sdk import AdfDataFlow


def test_adf_data_flow_good():
    test_node = AdfDataFlow(data_flow_id="96868946864896189", name="ADF Unit Test")
    assert test_node.get_name() == "ADF Unit Test"
    assert test_node.get_type() == "ADF_DATA_FLOW"
    assert test_node.get_fully_qualified_object_name() == "96868946864896189"
