from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class PowerBiDataFlowEntity(DataSet):
    """PowerBiDataFlowEntity's DataSet Class used for getting the required infomation for Pantomath
    :param group_id: The ID of the DataFlow's Group
    :type group_id: str
    :param object_id: The ID of the DataFlow
    :type object_id: str
    :param name: The name of the DataFlow
    :type name: str
    ...
    """

    def __init__(self, group_id, object_id, name):
        """Constructor method"""
        self._group_id = group_id
        self._object_id = object_id
        self._name = name

    @staticmethod
    def create(group_id, object_id, name):
        """Static method for obtaining PowerBiDataFlowEntity's DataSet Class
        used for getting the required infomation for Pantomath
        :param group_id: The ID of the DataFlow's Group
        :type group_id: str
        :param object_id: The ID of the DataFlow
        :type object_id: str
        :param name: The name of the DataFlow
        :type name: str
        ...
        :return: PowerBiDataFlowEntity class object
        :rtype: PowerBiDataFlowEntity
        """
        return PowerBiDataFlowEntity(group_id, object_id, name)

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
        return DataSetTypes.POWER_BI_DATAFLOW_ENTITY.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        fqn = str(
            "app.powerbi.com/groups/"
            + str(self._group_id)
            + "/dataflows/"
            + str(self._object_id)
            + "/syntheticEntity/"
            + self._name
        ).lower()
        return fqn
