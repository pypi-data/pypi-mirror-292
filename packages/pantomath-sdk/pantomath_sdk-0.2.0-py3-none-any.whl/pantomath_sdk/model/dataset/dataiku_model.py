from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes
import pantomath_sdk.util as util


class DataikuModel(DataSet):
    """DataikuModel's DataSet Class used for getting the required infomation for Pantomath
    :param host_name: the dataiku host
    :type host_name: str
    :param project_key: The project key that contains the dataset
    :type project_key: str
    :param model_name: Name of the model
    :type model_name: str
    :param model_id: ID of the model
    :type model_id: str
    ...
    """

    def __init__(self, host_name, project_key, model_name, model_id):
        """Constructor method"""
        self._host_name = host_name
        self._project_key = project_key
        self._model_name = model_name
        self._model_id = model_id

    @staticmethod
    def create(host_name, project_key, model_name, model_id):
        """Static method for obtaining DataikuModel's DataSet Class
        used for getting the required infomation for Pantomath
        :param host_name: the dataiku host
        :type host_name: str
        :param project_key: The project key that contains the dataset
        :type project_key: str
        :param model_name: Name of the model
        :type model_name: str
        :param model_id: ID of the model
        :type model_id: str
        ...
        :return: DataikuModel class object
        :rtype: DataikuModel
        """
        return DataikuModel(host_name, project_key, model_name, model_id)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return self._model_name

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return DataSetTypes.MODEL.value

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
                    + "/project/"
                    + str(self._project_key)
                    + "/models/"
                    + str(self._model_name)
                )
            )
        )
