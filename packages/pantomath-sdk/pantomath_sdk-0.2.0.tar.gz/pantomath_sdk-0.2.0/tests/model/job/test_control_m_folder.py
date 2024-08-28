from pantomath_sdk import ControlMFolder


def test_control_m_folder_good():
    node = ControlMFolder(
        host="mockHost",
        server="mockserver",
        folder_hierarchy=["A", "B"],
        name="ControlMFolder Unit Test",
    )
    assert node.get_name() == "ControlMFolder Unit Test"
    assert node.get_type() == "FOLDER"
    assert (
        node.get_fully_qualified_object_name()
        == "mockhost.mockserver.a.b.controlmfolder%20unit%20test"
    )


def test_control_m_folder_good_no_optional():
    node = ControlMFolder(
        host="mockHost",
        server="mockserver",
        name="ControlMFolder Unit Test",
    )
    assert node.get_name() == "ControlMFolder Unit Test"
    assert node.get_type() == "FOLDER"
    assert (
        node.get_fully_qualified_object_name()
        == "mockhost.mockserver.controlmfolder%20unit%20test"
    )
