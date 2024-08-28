from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes
import pantomath_sdk.util as util


class ControlMJob(Job):
    """ControlMJob's Job Class used for getting the required infomation for Pantomath
    :param host: host of the control m
    :type host: str
    :param server: name of the server
    :type server: str
    :param name: Name of the Job
    :type name: str
    :param folder_hierarchy: List of the Folders in order parent folder
    down to folder before this folder
    :type folder_hierarchy: list of strings
    ...
    """

    def __init__(self, host, server, name, folder_hierarchy=None):
        """Constructor method"""
        self._host = host
        self._server = server
        self._folder_hierarchy = folder_hierarchy
        self._name = name

    @staticmethod
    def create(host, server, name, folder_hierarchy):
        """Static method for obtaining ControlMJob's DataSet Class
        used for getting the required infomation for Pantomath
        :param host: host of the control m
        :type host: str
        :param server: name of the server
        :type server: str
        :param name: Name of the Job
        :type name: str
        :param folder_hierarchy: List of the Folders in order parent folder
        down to folder before this folder
        :type folder_hierarchy: list of strings
        ...
        :return: ControlMJob class object
        :rtype: ControlMJob
        """
        return ControlMJob(host, server, name, folder_hierarchy)

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
        return JobTypes.JOB.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        hierarchy = (
            ("." + ".".join(self._folder_hierarchy))
            if self._folder_hierarchy is not None
            else ""
        )
        return util.sanitize_fully_qualified_object_name(
            self._host + "." + self._server + hierarchy + "." + self.get_name()
        )
