from pantomath_sdk import AstroTask


def test_astro_task_good():
    node = AstroTask(
        host_name="https://testing.dev/astro_dags/",
        name="Astro Unit Test",
        dag_name="Unit Test Dag",
    )
    assert node.get_name() == "Astro Unit Test"
    assert node.get_type() == "TASK"
    assert (
        node.get_fully_qualified_object_name()
        == "https%3a//testing.dev/astro_dags//unit%20test%20dag/astro%20unit%20test"
    )
