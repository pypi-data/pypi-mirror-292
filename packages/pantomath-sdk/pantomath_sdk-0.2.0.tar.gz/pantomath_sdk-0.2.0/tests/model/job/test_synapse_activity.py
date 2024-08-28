from pantomath_sdk import SynapseActivity


def test_synapse_activity_good():
    node = SynapseActivity(
        name="SynapseActivity Unit Test", pipeline_id="3674798497356"
    )
    assert node.get_name() == "SynapseActivity Unit Test"
    assert node.get_type() == "ACTIVITY"
    assert (
        node.get_fully_qualified_object_name()
        == "3674798497356/activities/synapseactivity unit test"
    )
