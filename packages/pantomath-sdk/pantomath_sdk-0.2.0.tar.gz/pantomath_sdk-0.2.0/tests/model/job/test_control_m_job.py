from pantomath_sdk import ControlMJob


def test_control_m_folder_good():
    node = ControlMJob(
        host="mockHost",
        server="mockserver",
        folder_hierarchy=["A", "B", "C"],
        name="ControlMJob Unit Test",
    )
    assert node.get_name() == "ControlMJob Unit Test"
    assert node.get_type() == "JOB"
    assert (
        node.get_fully_qualified_object_name()
        == "mockhost.mockserver.a.b.c.controlmjob%20unit%20test"
    )


def test_control_m_folder_good_no_optional():
    node = ControlMJob(
        host="mockHost",
        server="mockserver",
        name="ControlMJob Unit Test",
    )
    assert node.get_name() == "ControlMJob Unit Test"
    assert node.get_type() == "JOB"
    assert (
        node.get_fully_qualified_object_name()
        == "mockhost.mockserver.controlmjob%20unit%20test"
    )
