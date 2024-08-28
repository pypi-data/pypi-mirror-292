from pantomath_sdk import PostJobRunLog
import pytest


def test_logs_good_data():
    mock_data_set = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
    }
    log = {
        "job_run_id": "jobRunId",
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "records_effected": 42,
        "target_data_sets": [mock_data_set],
        "source_data_sets": [mock_data_set],
        "iso_timestamp": "isoTimestamp",
    }
    log_data = PostJobRunLog(**log)
    assert log_data.validate_data()


def test_log_data_bad_tdataset():
    mock_data_set = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
    }
    log = {
        "job_run_id": "jobRunId",
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "records_effected": 42,
        "target_data_sets": "BAD_DATA",
        "source_data_sets": [mock_data_set],
        "iso_timestamp": "isoTimestamp",
    }
    with pytest.raises(TypeError):
        PostJobRunLog(log)


def test_send_log_data_bad_sdataset():
    mock_data_set = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
    }
    log = {
        "job_run_id": "jobRunId",
        "object_name": "objectName",
        "object_type": "objectType",
        "fullyQualifiedObjectName": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "records_effected": 42,
        "source_data_sets": "BAD_DATA",
        "target_data_sets": [mock_data_set],
        "iso_timestamp": "isoTimestamp",
    }
    with pytest.raises(TypeError):
        PostJobRunLog(log)


def test_send_log_data_no_optional():
    mock_data_set = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
    }
    log = {
        "job_run_id": "jobRunId",
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "source_data_sets": [mock_data_set],
        "target_data_sets": [mock_data_set],
        "iso_timestamp": "isoTimestamp",
    }
    with pytest.raises(TypeError):
        PostJobRunLog(log)


def test_send_log_data_bad_optional():
    mock_data_set = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
    }
    log = {
        "job_run_id": "jobRunId",
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "records_effected": "BAD_DATA",
        "source_data_sets": [mock_data_set],
        "target_data_sets": [mock_data_set],
        "iso_timestamp": "isoTimestamp",
    }
    with pytest.raises(TypeError):
        PostJobRunLog(log)


def test_send_log_data_missing_data():
    mock_data_set = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
    }
    log = {
        "object_name": "objectName",
        "object_type": "objectType",
        "fully_qualified_object_name": "fullyQualifiedObjectName",
        "status": "status",
        "message": "message",
        "records_effected": 42,
        "source_data_sets": [mock_data_set],
        "target_data_sets": [mock_data_set],
        "iso_timestamp": "isoTimestamp",
    }
    with pytest.raises(TypeError):
        PostJobRunLog(log)


def test_send_log_data_no_data():
    with pytest.raises(TypeError):
        PostJobRunLog(None)
