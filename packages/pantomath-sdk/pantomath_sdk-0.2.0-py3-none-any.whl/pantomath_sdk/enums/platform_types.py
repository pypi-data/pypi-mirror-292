from aenum import Enum


class PlatformTypes(Enum):
    """This class is an enum of all the PlatformTypes supported by the Pantomath Python SDK."""

    FIVETRAN = "FIVETRAN"
    SNOWFLAKE = "SNOWFLAKE"
    TABLEAU = "TABLEAU"
    UNKNOWN = "UNKNOWN"
    DBT = "DBT"
    IBM_DATASTAGE = "IBM_DATASTAGE"
    ADF = "ADF"
    POWERBI = "POWERBI"
    SSIS = "SSIS"
    SYNAPSE = "SYNAPSE"
    SSRS = "SSRS"
    SQL_SERVER = "SQL_SERVER"
    DBX = "DBX"
    AWS = "AWS"
    INFORMATICA = "INFORMATICA"
    PBIRS = "PBIRS"
    EXTERNAL = "EXTERNAL"
    AZSTORAGE = "AZSTORAGE"
    ORACLE = "ORACLE"
    DATAPROC = "DATAPROC"
    BIGQUERY = "BIGQUERY"
    COMPOSER = "COMPOSER"
    CUSTOM_LOGS = "CUSTOM_LOGS"

    @staticmethod
    def get_platform_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(PlatformTypes)[: len(PlatformTypes)]

    @staticmethod
    def is_platform_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in PlatformTypes.get_platform_types()
