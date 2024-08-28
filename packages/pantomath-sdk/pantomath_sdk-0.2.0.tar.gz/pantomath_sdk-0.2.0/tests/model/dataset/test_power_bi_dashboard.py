from pantomath_sdk import PowerBIDashboard


def test_powerbi_dashboard_good():
    test_node = PowerBIDashboard(
        workspace_id=123124124,
        dashboard_id=9879789789,
        name="powerbi_dashboard Unit Test",
    )
    assert test_node.get_name() == "powerbi_dashboard Unit Test"
    assert test_node.get_type() == "POWER_BI_DASHBOARD"
    assert (
        test_node.get_fully_qualified_object_name()
        == "app.powerbi.com/groups/123124124/dashboards/9879789789"
    )
