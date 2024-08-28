from pantomath_sdk import DataVolumeObjectTypes

expected_list = ["SQL_TABLE"]


def test_get_data_volume_object_types():
    statuses = DataVolumeObjectTypes.get_data_volume_object_types()
    assert statuses.sort() == expected_list.sort()


def test_is_data_volume_object_type():
    assert DataVolumeObjectTypes.is_data_volume_object_type("SQL_TABLE")


def test_not_is_data_volume_object_type():
    assert not DataVolumeObjectTypes.is_data_volume_object_type("FOO")
