from pantomath_sdk import PlatformTypes


def test_get_platform_types():
    expected_list = [
        "FIVETRAN",
        "SNOWFLAKE",
        "TABLEAU",
        "UNKNOWN",
        "DBT",
        "IBM_DATASTAGE",
        "ADF",
        "POWERBI",
        "SSIS",
        "SYNAPSE",
        "SSRS",
        "SQL_SERVER",
        "DBX",
        "AWS",
        "INFORMATICA",
        "PBIRS",
        "EXTERNAL",
        "AZSTORAGE",
        "ORACLE",
        "DATAPROC",
        "BIGQUERY",
        "COMPOSER",
        "CUSTOM_LOGS",
    ]
    statuses = PlatformTypes.get_platform_types()
    assert statuses.sort() == expected_list.sort()


def test_is_platform_type():
    assert PlatformTypes.is_platform_type("SQL_SERVER")


def test_not_is_platform_type():
    assert not PlatformTypes.is_platform_type("FOO")
