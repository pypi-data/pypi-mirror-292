from pantomath_sdk import DataikuProject


def test_dataiku_project_good():
    test_node = DataikuProject(
        host_name="host",
        project_key="96868946864896189",
        project_label="DataikuProject Unit Test",
    )
    assert test_node.get_name() == "DataikuProject Unit Test"
    assert test_node.get_type() == "PROJECT"
    assert (
        test_node.get_fully_qualified_object_name() == "host/projects/96868946864896189"
    )
