from pantomath_sdk import SSISTask


def test_ssis_task_good():
    node = SSISTask(
        executable_name="_executableName",
        parent_executable_name="_parentExecutableName",
        project_name="projectName",
        folder_name="_folderName",
    )
    assert node.get_name() == "_executableName"
    assert node.get_type() == "TASK"
    assert (
        node.get_fully_qualified_object_name()
        == "_foldername.projectname._parentexecutablename._executablename"
    )
