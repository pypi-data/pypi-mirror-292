from aenum import Enum


class JobTypes(Enum):
    """This class is an enum of all the JobTypes supported by the Pantomath Python SDK."""

    DAG = "DAG"
    SQL_FUNCTION = "SQL_FUNCTION"
    SQL_PROCEDURE = "SQL_PROCEDURE"
    TABLEAU_EXTRACT_REFRESH_TASK = "TABLEAU_EXTRACT_REFRESH_TASK"
    FIVETRAN_CONNECTOR = "FIVETRAN_CONNECTOR"
    DBT_MODEL = "DBT_MODEL"
    POWER_BI_REFRESH = "POWER_BI_REFRESH"
    POWER_BI_DATAFLOW = "POWER_BI_DATAFLOW"
    ADF_ACTIVITY = "ADF_ACTIVITY"
    ADF_PIPELINE = "ADF_PIPELINE"
    JOB = "JOB"
    ACTIVITY = "ACTIVITY"
    PIPELINE = "PIPELINE"
    PACKAGE = "PACKAGE"
    COMPONENT = "COMPONENT"
    TASK = "TASK"
    SNOWFLAKE_PIPE = "SNOWFLAKE_PIPE"
    AWS_LAMBDA = "AWS_LAMBDA"
    PROJECT = "PROJECT"
    RECIPE = "RECIPE"
    FOLDER = "FOLDER"

    @staticmethod
    def get_job_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(JobTypes)[: len(JobTypes)]

    @staticmethod
    def is_job_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in JobTypes.get_job_types()
