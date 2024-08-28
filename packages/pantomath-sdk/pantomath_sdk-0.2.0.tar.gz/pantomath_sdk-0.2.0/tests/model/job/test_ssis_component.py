from pantomath_sdk import SSISComponent


def test_ssis_component_good():
    node = SSISComponent(
        name="SSISComponent Unit Test",
        folder_name="_folderName",
        execution_path="_executionPath",
        project_name="projectName",
    )
    assert node.get_name() == "SSISComponent Unit Test"
    assert node.get_type() == "COMPONENT"
    assert (
        node.get_fully_qualified_object_name()
        == "_foldername.projectname._executionpath.ssiscomponent unit test"
    )
