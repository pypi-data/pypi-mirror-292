from pantomath_sdk import PantomathSDK
from pantomath_sdk import AstroDag
from pantomath_sdk import DataikuDataset

good_job = AstroDag(name="TestJob", host_name="testHost")
mock_data_set = DataikuDataset(
    host_name="host_name",
    project_key="project_key",
    dataset_name="dataset_name",
)
good_job_run_log = {
    "job": good_job,
    "name": "TestJobRunLog",
    "source_data_sets": [mock_data_set],
    "target_data_sets": [mock_data_set],
    "next_run_at": "next_run_at",
}


def test_pantomath_sdk_good():
    sdk = PantomathSDK(
        api_base_url="api_base_url_1",
        api_key="api_key_1",
    )
    assert sdk._api_base_url == "api_base_url_1"
    assert sdk._api_key == "api_key_1"


def test_pantomath_sdk_new_job_run_good():
    sdk = PantomathSDK(
        api_base_url="api_base_url_1",
        api_key="api_key_1",
    )
    test_job_run = sdk.new_job_run(
        job=good_job,
        name="name",
        next_run_at="next_run_at",
        source_data_sets=[mock_data_set],
        target_data_sets=[mock_data_set],
    )
    assert (
        test_job_run._get_normalized_message("Hello")
        == "name running in TestJob: Hello"
    )
    post_job = test_job_run.get_job()
    assert post_job == good_job
    testDataSet = test_job_run.get_source_data_sets()
    assert testDataSet[0] == {
        "objectName": mock_data_set.get_name(),
        "objectType": mock_data_set.get_type(),
        "fullyQualifiedObjectName": mock_data_set.get_fully_qualified_object_name(),
    }
    testDataSet = test_job_run.get_target_data_sets()
    assert testDataSet[0] == {
        "objectName": mock_data_set.get_name(),
        "objectType": mock_data_set.get_type(),
        "fullyQualifiedObjectName": mock_data_set.get_fully_qualified_object_name(),
    }
    assert test_job_run.get_next_run_at() == "next_run_at"
