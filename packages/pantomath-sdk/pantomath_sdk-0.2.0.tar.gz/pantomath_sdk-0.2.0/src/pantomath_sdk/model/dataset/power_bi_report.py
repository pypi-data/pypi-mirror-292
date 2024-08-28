from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class PowerBIReport(DataSet):
    """PowerBIReport's DataSet Class used for getting the required infomation for Pantomath
    :param report_id: The ID of the Report
    :type report_id: str
    :param workspace_id: The ID of the Workspace
    :type workspace_id: str
    :param name: The name of the Data Set
    :type name: str
    ...
    """

    def __init__(self, report_id, workspace_id, name):
        """Constructor method"""
        self._report_id = report_id
        self._workspace_id = workspace_id
        self._name = name

    @staticmethod
    def create(report_id, workspace_id, name):
        """Static method for obtaining PowerBIReport's DataSet Class
        used for getting the required infomation for Pantomath
        :param report_id: The ID of the Report
        :type report_id: str
        :param workspace_id: The ID of the Workspace
        :type workspace_id: str
        :param name: The name of the Data Set
        :type name: str
        ...
        :return: PowerBIReport class object
        :rtype: PowerBIReport
        """
        return PowerBIReport(report_id, workspace_id, name)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return self._name

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return DataSetTypes.POWER_BI_REPORT.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        fqn = str(
            "app.powerbi.com/groups/"
            + str(self._workspace_id)
            + "/reports/"
            + str(self._report_id)
            + "/ReportSection"
        ).lower()
        return fqn
