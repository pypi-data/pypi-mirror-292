from pantomath_sdk import PowerBiDataFlow


def test_power_bi_data_flow_good():
    node = PowerBiDataFlow(
        name="PowerBiDataFlow Unit Test",
        group_id="245632457634",
        object_id="5785678976809",
    )
    assert node.get_name() == "PowerBiDataFlow Unit Test"
    assert node.get_type() == "POWER_BI_DATAFLOW"
    assert (
        node.get_fully_qualified_object_name()
        == "app.powerbi.com/groups/245632457634/dataflows/5785678976809"
    )
