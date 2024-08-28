from pantomath_sdk import (
    TableauExtractRefreshTask,
)


def test_tableau_extract_refresh_task_good():
    node = TableauExtractRefreshTask(
        name="TableauExtractRefreshTask Unit Test",
        site_id="site_id",
        refresh_id="refresh_id",
        host="host",
    )
    assert node.get_name() == "TableauExtractRefreshTask Unit Test"
    assert node.get_type() == "TABLEAU_EXTRACT_REFRESH_TASK"
    assert node.get_fully_qualified_object_name() == "host/site/site_id/task/refresh_id"
