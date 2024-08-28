from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class SSISPackage(Job):
    """SSISPackage's Job Class used for getting the required infomation for Pantomath
    :param project_name: Name of the Project
    :type project_name: str
    :param folder_name: Name of the Folder
    :type folder_name: str
    :param name: Name of the Package
    :type name: str
    ...
    """

    def __init__(self, project_name, folder_name, name):
        """Constructor method"""
        self._name = name
        self._folder_name = folder_name
        self._project_name = project_name

    @staticmethod
    def create(project_name, folder_name, name):
        """Static method for obtaining SSISPackage's DataSet Class
        used for getting the required infomation for Pantomath
        :param project_name: Name of the Project
        :type project_name: str
        :param folder_name: Name of the Folder
        :type folder_name: str
        :param name: Name of the Package
        :type name: str
        ...
        :return: SSISPackage class object
        :rtype: SSISPackage
        """
        return SSISPackage(project_name, folder_name, name)

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
        return JobTypes.PACKAGE.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(
            self._folder_name + "." + self._project_name + "." + self._name
        ).lower()
