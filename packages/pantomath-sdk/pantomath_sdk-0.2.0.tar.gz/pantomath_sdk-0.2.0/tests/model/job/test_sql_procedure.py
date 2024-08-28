from pantomath_sdk import SqlProcedure


def test_sql_procedure_good():
    node = SqlProcedure(
        name="SqlProcedure Unit Test",
        schema="schema",
        database="database",
        port=42,
        host="host",
    )
    assert node.get_name() == "SqlProcedure Unit Test"
    assert node.get_type() == "SQL_PROCEDURE"
    assert (
        node.get_fully_qualified_object_name()
        == "host:42.database.schema.SqlProcedure Unit Test"
    )
