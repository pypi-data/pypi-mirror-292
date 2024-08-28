from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes
import pantomath_sdk.util as util


class AstroDag(Job):
    """AstroDag's Job Class used for getting the required infomation for Pantomath
    :param host_name: NAme of the host
    :type host_name: str
    :param name: Name of the DAG
    :type name: str
    ...
    """

    def __init__(self, host_name, name):
        """Constructor method"""
        self._host_name = host_name
        self._name = name

    @staticmethod
    def create(host_name, name):
        """Static method for obtaining AstroDag's DataSet Class
        used for getting the required infomation for Pantomath
        :param host_name: NAme of the host
        :type host_name: str
        :param name: Name of the DAG
        :type name: str
        ...
        :return: AstroDag class object
        :rtype: AstroDag
        """
        return AstroDag(host_name, name)

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
        return JobTypes.DAG.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(
            self._host_name + "/" + self.get_name()
        )
