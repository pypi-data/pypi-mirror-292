from pantomath_sdk import TableauWorkbook


def test_powerbi_report_good():
    test_node = TableauWorkbook(
        host="host",
        uri="uri",
        name="TableauWorkbook Unit Test",
    )
    assert test_node.get_name() == "TableauWorkbook Unit Test"
    assert test_node.get_type() == "TABLEAU_WORKBOOK"
    assert test_node.get_fully_qualified_object_name() == "host/uri"
