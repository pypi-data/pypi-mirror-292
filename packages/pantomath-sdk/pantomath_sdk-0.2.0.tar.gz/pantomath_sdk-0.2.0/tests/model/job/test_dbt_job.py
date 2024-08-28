from pantomath_sdk import DBTJobConstructor


def test_dbt_job_good():
    node = DBTJobConstructor(
        account_id=146523457734567,
        name="DBTJobConstructor Unit Test",
        job_id=12453576758,
        project_name="DBTJobConstructor Project",
    )
    assert node.get_name() == "DBTJobConstructor Unit Test"
    assert node.get_type() == "JOB"
    assert (
        node.get_fully_qualified_object_name()
        == "cloud.getdbt.com/#/accounts/146523457734567.dbtjobconstructor project."
        "dbtjobconstructor unit test.12453576758"
    )
