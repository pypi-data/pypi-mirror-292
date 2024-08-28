from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class FivetranConnectorConstructor(Job):
    """FivetranConnectorConstructor's Job Class
    used for getting the required infomation for Pantomath
    :param name: Name of the Constructor
    :type name: str
    ...
    """

    def __init__(self, name):
        """Constructor method"""
        self._name = name

    @staticmethod
    def create(name):
        """Static method for obtaining FivetranConnectorConstructor's DataSet Class
        used for getting the required infomation for Pantomath
        :param name: Name of the Constructor
        :type name: str
        ...
        :return: FivetranConnectorConstructor class object
        :rtype: FivetranConnectorConstructor
        """
        return FivetranConnectorConstructor(name)

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
        return JobTypes.FIVETRAN_CONNECTOR.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(self._name)
