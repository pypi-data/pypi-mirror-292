from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes
import pantomath_sdk.util as util


class AdfDataFlow(DataSet):
    """AdfDataFlow's DataSet Class used for getting the required infomation for Pantomath
    :param data_flow_id: The ID of the data flow
    :type data_flow_id: str
    :param name: Name of the data flow
    :type name: str
    ...
    """

    def __init__(self, data_flow_id, name):
        """Constructor method"""
        self._data_flow_id = data_flow_id
        self._name = name

    @staticmethod
    def create(**kwargs):
        """Static method for obtaining AdfDataFlow's DataSet Class
        used for getting the required infomation for Pantomath
        :param data_flow_id: The ID of the data flow
        :type data_flow_id: str
        :param data_flow_id: Name of the data flow
        :type data_flow_id: str
        ...
        :return: AdfDataFlow class object
        :rtype: AdfDataFlow
        """
        return AdfDataFlow(**kwargs)

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
        return DataSetTypes.ADF_DATA_FLOW.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(self._data_flow_id)
