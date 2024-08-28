from aenum import Enum


class JobObjectTypes(Enum):
    """This class is an enum of all the Jobs supported by the Pantomath Python SDK."""

    SQL_FUNCTION = "SQL_FUNCTION"
    SQL_PROCEDURE = "SQL_PROCEDURE"
    TABLEAU_EXTRACT_REFRESH_TASK = "TABLEAU_EXTRACT_REFRESH_TASK"
    FIVETRAN_CONNECTOR = "FIVETRAN_CONNECTOR"
    DBT_MODEL = "DBT_MODEL"
    POWER_BI_REFRESH = "POWER_BI_REFRESH"
    POWER_BI_ACTIVITY = "POWER_BI_ACTIVITY"
    POWER_BI_DATAFLOW = "POWER_BI_DATAFLOW"
    ADF_ACTIVITY = "ADF_ACTIVITY"
    ADF_PIPELINE = "ADF_PIPELINE"
    JOB = "JOB"
    ACTIVITY = "ACTIVITY"
    DATAFLOW = "DATAFLOW"
    PIPELINE = "PIPELINE"
    PACKAGE = "PACKAGE"
    COMPONENT = "COMPONENT"
    REFRESH = "REFRESH"
    TASK = "TASK"
    SNOWFLAKE_PIPE = "SNOWFLAKE_PIPE"

    @staticmethod
    def get_job_object_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(JobObjectTypes)[: len(JobObjectTypes)]

    @staticmethod
    def is_job_object_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in JobObjectTypes.get_job_object_types()
