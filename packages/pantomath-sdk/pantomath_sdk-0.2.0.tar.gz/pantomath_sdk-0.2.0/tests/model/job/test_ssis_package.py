from pantomath_sdk import SSISPackage


def test_ssis_package_good():
    node = SSISPackage(
        name="SSISPackage Unit Test",
        folder_name="_folderName",
        project_name="projectName",
    )
    assert node.get_name() == "SSISPackage Unit Test"
    assert node.get_type() == "PACKAGE"
    assert (
        node.get_fully_qualified_object_name()
        == "_foldername.projectname.ssispackage unit test"
    )
