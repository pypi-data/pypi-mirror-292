from pantomath_sdk import PowerBIReport


def test_powerbi_report_good():
    test_node = PowerBIReport(
        workspace_id=123124124,
        report_id=9879789789,
        name="PowerBIReport Unit Test",
    )
    assert test_node.get_name() == "PowerBIReport Unit Test"
    assert test_node.get_type() == "POWER_BI_REPORT"
    assert (
        test_node.get_fully_qualified_object_name()
        == "app.powerbi.com/groups/123124124/reports/9879789789/reportsection"
    )
