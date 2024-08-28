from pantomath_sdk import SqlMaterializedView


def test_powerbi_report_good():
    test_node = SqlMaterializedView(
        host="host",
        port=42,
        database="database",
        schema="Schema",
        name="SqlMaterializedView Unit Test",
    )
    assert test_node.get_name() == "SqlMaterializedView Unit Test"
    assert test_node.get_type() == "SQL_MATERIALIZED_VIEW"
    assert (
        test_node.get_fully_qualified_object_name()
        == "host:42.database.Schema.SqlMaterializedView Unit Test"
    )
