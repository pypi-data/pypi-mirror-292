from pantomath_sdk import DBTModelConstructor


def test_dbt_model_good():
    node = DBTModelConstructor(
        dbt_root_name="Root",
        account_id=146523457734567,
        package_name="package",
        job_name="DBTModelConstructor Unit Test",
        job_database_name="database",
        job_schema_name="schema",
    )
    assert node.get_name() == "DBTModelConstructor Unit Test Model"
    assert node.get_type() == "DBT_MODEL"
    assert (
        node.get_fully_qualified_object_name()
        == "root146523457734567.package.database.schema.dbtmodelconstructor unit test"
    )
