from pantomath_sdk import SqlFunction


def test_sql_function_good():
    node = SqlFunction(
        name="SqlFunction Unit Test",
        schema="schema",
        database="database",
        port=42,
        host="host",
    )
    assert node.get_name() == "SqlFunction Unit Test"
    assert node.get_type() == "SQL_FUNCTION"
    assert (
        node.get_fully_qualified_object_name()
        == "host:42.database.schema.SqlFunction Unit Test"
    )
