from pantomath_sdk import SqlTable


def test_powerbi_report_good():
    test_node = SqlTable(
        host="host",
        port=42,
        database="database",
        schema="Schema",
        name="SqlTable Unit Test",
    )
    assert test_node.get_name() == "SqlTable Unit Test"
    assert test_node.get_type() == "SQL_TABLE"
    assert (
        test_node.get_fully_qualified_object_name()
        == "host:42.database.Schema.SqlTable Unit Test"
    )
