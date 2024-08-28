from pantomath_sdk import S3Bucket


def test_powerbi_report_good():
    test_node = S3Bucket(s3_bucket="S3 Bucket Unit Test")
    assert test_node.get_name() == "S3 Bucket Unit Test"
    assert test_node.get_type() == "S3_BUCKET"
    assert test_node.get_fully_qualified_object_name() == "S3 Bucket Unit Test"
