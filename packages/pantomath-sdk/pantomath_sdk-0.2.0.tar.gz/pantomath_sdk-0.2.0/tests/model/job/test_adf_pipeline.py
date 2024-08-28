from pantomath_sdk import ADFPipeline


def test_adf_pipeline_good():
    node = ADFPipeline(
        pipeline_id=13465478579,
        name="ADFPipeline Unit Test",
    )
    assert node.get_name() == "ADFPipeline Unit Test"
    assert node.get_type() == "ADF_PIPELINE"
    assert node.get_fully_qualified_object_name() == "13465478579"
