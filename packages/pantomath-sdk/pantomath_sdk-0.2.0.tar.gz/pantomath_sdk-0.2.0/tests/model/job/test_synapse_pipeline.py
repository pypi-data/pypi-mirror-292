from pantomath_sdk import SynapsePipeline


def test_synapse_pipeline_good():
    node = SynapsePipeline(
        name="SynapsePipeline Unit Test", pipeline_id="3674798497356"
    )
    assert node.get_name() == "SynapsePipeline Unit Test"
    assert node.get_type() == "PIPELINE"
    assert node.get_fully_qualified_object_name() == "3674798497356"
