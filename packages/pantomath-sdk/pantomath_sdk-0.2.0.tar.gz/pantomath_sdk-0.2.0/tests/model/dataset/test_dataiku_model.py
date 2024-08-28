from pantomath_sdk import DataikuModel


def test_dataiku_model_good():
    test_node = DataikuModel(
        host_name="host",
        project_key="96868946864896189",
        model_name="DataikuModel Unit Test",
        model_id=3456745457,
    )
    assert test_node.get_name() == "DataikuModel Unit Test"
    assert test_node.get_type() == "MODEL"
    assert (
        test_node.get_fully_qualified_object_name()
        == "host/project/96868946864896189/models/dataikumodel%20unit%20test"
    )
