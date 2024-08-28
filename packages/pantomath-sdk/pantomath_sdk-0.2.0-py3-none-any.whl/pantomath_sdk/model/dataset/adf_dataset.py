from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes
import pantomath_sdk.util as util


class ADFDataset(DataSet):
    """ADFDataset's DataSet Class used for getting the required infomation for Pantomath
    :param data_set_id: The ID of the data set
    :type data_set_id: str
    :param name: Name of the data set
    :type name: str
    ...
    """

    def __init__(self, data_set_id, name):
        """Constructor method"""
        self._data_set_id = data_set_id
        self._name = name

    @staticmethod
    def create(data_set_id, name):
        """Static method for obtaining ADFDataset's DataSet Class
        used for getting the required infomation for Pantomath
        :param data_set_id: The ID of the data set
        :type data_set_id: str
        :param name: Name of the data set
        :type name: str
        ...
        :return: ADFDataset class object
        :rtype: ADFDataset
        """
        return ADFDataset(data_set_id, name)

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
        return DataSetTypes.ADF_DATASET.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(self._data_set_id)
