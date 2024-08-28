from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class PowerBIDataset(DataSet):
    """PowerBIDataset's DataSet Class used for getting the required infomation for Pantomath
    :param dashboard_id: The ID of the Dashboard
    :type dashboard_id: str
    :param workspace_id: The ID of the Workspace
    :type workspace_id: str
    :param name: The name of the Data Set
    :type name: str
    ...
    """

    def __init__(self, dashboard_id, workspace_id, name):
        """Constructor method"""
        self._dataset_id = dashboard_id
        self._workspace_id = workspace_id
        self._name = name

    @staticmethod
    def create(dashboard_id, workspace_id, name):
        """Static method for obtaining PowerBIDataset's DataSet Class
        used for getting the required infomation for Pantomath
        :param dashboard_id: The ID of the Dashboard
        :type dashboard_id: str
        :param workspace_id: The ID of the Workspace
        :type workspace_id: str
        :param name: The name of the Data Set
        :type name: str
        ...
        :return: PowerBIDataset class object
        :rtype: PowerBIDataset
        """
        return PowerBIDataset(dashboard_id, workspace_id, name)

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
        return DataSetTypes.POWER_BI_DATASET.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        fqn = str(
            "app.powerbi.com/groups/"
            + str(self._workspace_id)
            + "/datasets/"
            + str(self._dataset_id)
        ).lower()
        return fqn
