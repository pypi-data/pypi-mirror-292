from pantomath_sdk import AWSLambda


def test_aws_lambda_good():
    node = AWSLambda(
        name="AWSLambda Unit Test",
    )
    assert node.get_name() == "AWSLambda Unit Test"
    assert node.get_type() == "AWS_LAMBDA"
    assert node.get_fully_qualified_object_name() == "AWSLambda Unit Test"
