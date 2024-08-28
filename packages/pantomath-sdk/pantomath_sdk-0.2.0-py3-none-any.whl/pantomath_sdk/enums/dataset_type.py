from aenum import Enum


class DataSetTypes(Enum):
    """This class is an enum of all the DataSets supported by the Pantomath Python SDK."""

    SQL_TABLE = "SQL_TABLE"
    SQL_VIEW = "SQL_VIEW"
    SQL_MATERIALIZED_VIEW = "SQL_MATERIALIZED_VIEW"
    S3_BUCKET = "S3_BUCKET"
    TABLEAU_WORKBOOK = "TABLEAU_WORKBOOK"
    TABLEAU_DATASOURCE = "TABLEAU_DATASOURCE"
    POWER_BI_DASHBOARD = "POWER_BI_DASHBOARD"
    POWER_BI_REPORT = "POWER_BI_REPORT"
    POWER_BI_DATASET = "POWER_BI_DATASET"
    POWER_BI_DATAFLOW_ENTITY = "POWER_BI_DATAFLOW_ENTITY"
    ADF_DATA_FLOW = "ADF_DATA_FLOW"
    ADF_DATASET = "ADF_DATASET"
    FTP = "FTP"
    DATASET = "DATASET"
    MODEL = "MODEL"

    @staticmethod
    def get_dataset_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(DataSetTypes)[: len(DataSetTypes)]

    @staticmethod
    def is_dataset_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in DataSetTypes.get_dataset_types()
