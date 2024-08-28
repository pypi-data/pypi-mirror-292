from pantomath_sdk import FivetranConnectorConstructor


def test_fivetran_connector_constructor_good():
    node = FivetranConnectorConstructor(
        name="FivetranConnectorConstructor Unit Test",
    )
    assert node.get_name() == "FivetranConnectorConstructor Unit Test"
    assert node.get_type() == "FIVETRAN_CONNECTOR"
    assert (
        node.get_fully_qualified_object_name()
        == "FivetranConnectorConstructor Unit Test"
    )
