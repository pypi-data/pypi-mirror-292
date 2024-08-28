from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes
import pantomath_sdk.util as util


class DataikuDataset(DataSet):
    """DataikuDataset's DataSet Class used for getting the required infomation for Pantomath
    :param host_name: the dataiku host
    :type host_name: str
    :param project_key: The project key that contains the dataset
    :type project_key: str
    :param dataset_name: Name of the data set
    :type dataset_name: str
    ...
    """

    def __init__(self, host_name, project_key, dataset_name):
        """Constructor method"""
        self._host_name = host_name
        self._project_key = project_key
        self._dataset_name = dataset_name

    @staticmethod
    def create(host_name, project_key, dataset_name):
        """Static method for obtaining DataikuDataset's DataSet Class
        used for getting the required infomation for Pantomath
        :param host_name: the dataiku host
        :type host_name: str
        :param project_key: The project key that contains the dataset
        :type project_key: str
        :param dataset_name: Name of the data set
        :type dataset_name: str
        ...
        :return: DataikuDataset class object
        :rtype: DataikuDataset
        """
        return DataikuDataset(host_name, project_key, dataset_name)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return self._dataset_name

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return DataSetTypes.DATASET.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(
            util.normalize_host(
                str(
                    str(self._host_name)
                    + "/projects/"
                    + str(self._project_key)
                    + "/datasets/"
                    + str(self._dataset_name)
                )
            )
        )
