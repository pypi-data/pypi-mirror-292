from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes
import pantomath_sdk.util as util


class TableauDatasource(DataSet):
    """TableauDatasource's DataSet Class used for getting the required infomation for Pantomath
    :param host: The Tableau Host
    :type host: str
    :param uri: Tableau uri
    :type uri: str
    :param name: Name of the datasource
    :type name: str
    ...
    """

    def __init__(self, host, uri, name):
        """Constructor method"""
        self._host = host
        self._uri = uri
        self._name = name

    @staticmethod
    def create(host, uri, name):
        """Static method for obtaining TableauDatasource's DataSet Class
        used for getting the required infomation for Pantomath
        :param host: The Tableau Host
        :type host: str
        :param uri: Tableau uri
        :type uri: str
        :param name: Name of the datasource
        :type name: str
        ...
        :return: TableauDatasource class object
        :rtype: TableauDatasource
        """
        return TableauDatasource(host, uri, name)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return util.sanitize_tableau_string(self._name)

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return DataSetTypes.TABLEAU_DATASOURCE.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(util.normalize_host(self._host) + "/" + self._uri).lower()
