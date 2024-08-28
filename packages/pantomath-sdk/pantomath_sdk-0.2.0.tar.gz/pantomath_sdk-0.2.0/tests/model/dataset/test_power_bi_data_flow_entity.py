from pantomath_sdk import PowerBiDataFlowEntity


def test_powerbi_dataflow_entity_good():
    test_node = PowerBiDataFlowEntity(
        group_id=123124124,
        object_id=9879789789,
        name="powerbi_dataflow_entity Unit Test",
    )
    assert test_node.get_name() == "powerbi_dataflow_entity Unit Test"
    assert test_node.get_type() == "POWER_BI_DATAFLOW_ENTITY"
    assert (
        test_node.get_fully_qualified_object_name()
        == "app.powerbi.com/groups/123124124/dataflows/9879789789/syntheticentity/"
        "powerbi_dataflow_entity unit test"
    )
