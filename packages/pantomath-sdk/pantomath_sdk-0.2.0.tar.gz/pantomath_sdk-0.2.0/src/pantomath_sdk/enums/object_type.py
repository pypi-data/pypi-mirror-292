from aenum import Enum


class ObjectType(Enum):
    """This class is an enum of all the ObjectType supported by the Pantomath Python SDK."""

    SQL_TABLE = "SQL_TABLE"
    SQL_VIEW = "SQL_VIEW"
    SQL_MATERIALIZED_VIEW = "SQL_MATERIALIZED_VIEW"
    SQL_FUNCTION = "SQL_FUNCTION"
    SQL_PROCEDURE = "SQL_PROCEDURE"
    S3_BUCKET = "S3_BUCKET"
    TABLEAU_EXTRACT_REFRESH_TASK = "TABLEAU_EXTRACT_REFRESH_TASK"
    TABLEAU_WORKBOOK = "TABLEAU_WORKBOOK"
    TABLEAU_DATASOURCE = "TABLEAU_DATASOURCE"
    SNOWFLAKE_PIPE = "SNOWFLAKE_PIPE"
    FIVETRAN_CONNECTOR = "FIVETRAN_CONNECTOR"
    UNKNOWN = "UNKNOWN"
    DBT_MODEL = "DBT_MODEL"
    POWER_BI_DASHBOARD = "POWER_BI_DASHBOARD"
    POWER_BI_REPORT = "POWER_BI_REPORT"
    POWER_BI_DATASET = "POWER_BI_DATASET"
    POWER_BI_DATAFLOW_ENTITY = "POWER_BI_DATAFLOW_ENTITY"
    POWER_BI_REFRESH = "POWER_BI_REFRESH"
    POWER_BI_DATAFLOW = "POWER_BI_DATAFLOW"
    POWER_BI_ACTIVITY = "POWER_BI_ACTIVITY"
    ADF_ACTIVITY = "ADF_ACTIVITY"
    ADF_DATA_FLOW = "ADF_DATA_FLOW"
    ADF_PIPELINE = "ADF_PIPELINE"
    ADF_DATASET = "ADF_DATASET"
    SYNAPSE_DATAFLOW = "SYNAPSE_DATAFLOW"
    PACKAGE = "PACKAGE"
    COMPONENT = "COMPONENT"
    JOB = "JOB"
    DATASOURCE = "DATASOURCE"
    DATASET = "DATASET"
    DATAFLOW = "DATAFLOW"
    ACTIVITY = "ACTIVITY"
    PIPELINE = "PIPELINE"
    REPORT = "REPORT"
    TRIGGER = "TRIGGER"
    REFRESH = "REFRESH"
    TASK = "TASK"

    @staticmethod
    def get_object_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(ObjectType)[: len(ObjectType)]

    @staticmethod
    def is_object_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in ObjectType.get_object_types()
