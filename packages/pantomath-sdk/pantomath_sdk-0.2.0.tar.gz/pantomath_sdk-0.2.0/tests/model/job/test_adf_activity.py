from pantomath_sdk import ADFActivity


def test_adf_activity_good():
    node = ADFActivity(
        pipeline_id=13465478579,
        name="ADFActivity Unit Test",
    )
    assert node.get_name() == "ADFActivity Unit Test"
    assert node.get_type() == "ADF_ACTIVITY"
    assert (
        node.get_fully_qualified_object_name()
        == "13465478579/activities/adfactivity%20unit%20test"
    )
