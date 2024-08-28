from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class PowerBIDashboard(DataSet):
    """PowerBIDashboard's DataSet Class used for getting the required infomation for Pantomath
    :param dashboard_id: The ID of the Dashboard
    :type dashboard_id: str
    :param workspace_id: The ID of the Workspace
    :type workspace_id: str
    :param name: The name of the Dashboard
    :type name: str
    ...
    """

    def __init__(self, dashboard_id, workspace_id, name):
        """Constructor method"""
        self._dashboard_id = dashboard_id
        self._workspace_id = workspace_id
        self._name = name

    @staticmethod
    def create(dashboard_id, workspace_id, name):
        """Static method for obtaining PowerBIDashboard's DataSet Class
        used for getting the required infomation for Pantomath
        :param dashboard_id: The ID of the Dashboard
        :type dashboard_id: str
        :param workspace_id: The ID of the Workspace
        :type workspace_id: str
        :param name: The name of the Dashboard
        :type name: str
        ...
        :return: PowerBIDashboard class object
        :rtype: PowerBIDashboard
        """
        return PowerBIDashboard(dashboard_id, workspace_id, name)

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
        return DataSetTypes.POWER_BI_DASHBOARD.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        fqn = str(
            "app.powerbi.com/groups/"
            + str(self._workspace_id)
            + "/dashboards/"
            + str(self._dashboard_id)
        ).lower()
        return fqn
