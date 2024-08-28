from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class FTP(DataSet):
    """File Transfer Protocol (FTP)'s DataSet Class
    used for getting the required infomation for Pantomath
    :param uri: uri of the FTP
    :type uri: str
    :param name: Name of the FTP
    :type name: str
    ...
    """

    def __init__(self, uri, name):
        """Constructor method"""
        self._uri = uri
        self._name = name

    @staticmethod
    def create(uri, name):
        """Static method for obtaining File Transfer Protocol's DataSet Class
        used for getting the required infomation for Pantomath
        :param uri: uri of the FTP
        :type uri: str
        :param name: Name of the FTP
        :type name: str
        ...
        :return: File Transfer Protocol class object
        :rtype: File Transfer Protocol
        """
        return FTP(uri, name)

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
        return DataSetTypes.FTP.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return self._uri
