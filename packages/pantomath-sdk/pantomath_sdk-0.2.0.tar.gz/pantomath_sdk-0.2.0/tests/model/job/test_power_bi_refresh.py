from pantomath_sdk import PowerBIRefresh


def test_power_bi_refresh_good():
    node = PowerBIRefresh(
        name="PowerBIRefresh Unit Test",
        refresh_schedule_context="refresh_schedule_context",
        dataset_id="5785678976809",
    )
    assert node.get_name() == "PowerBIRefresh Unit Test"
    assert node.get_type() == "POWER_BI_REFRESH"
    assert (
        node.get_fully_qualified_object_name()
        == "refresh_schedule_context/5785678976809/powerbirefresh_unit_test"
    )
