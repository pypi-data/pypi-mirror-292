from pantomath_sdk import SnowflakePipe


def test_snowflake_pipe_good():
    node = SnowflakePipe(
        name="SnowflakePipe Unit Test",
        schema="schema",
        database="database",
        port=42,
        host="host",
    )
    assert node.get_name() == "SnowflakePipe Unit Test"
    assert node.get_type() == "SNOWFLAKE_PIPE"
    assert (
        node.get_fully_qualified_object_name()
        == "host:42.database.schema.SnowflakePipe Unit Test"
    )
