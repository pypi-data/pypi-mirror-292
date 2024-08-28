from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes

DBT_ROOT_NAME_DEFAULT = "cloud.getdbt.com/#/accounts/"


class DBTJobConstructor(Job):
    """DBTJobConstructor's Job Class used for getting the required infomation for Pantomath
    :param name: Name of the Job
    :type name: str
    :param account_id: ID of the Account
    :type account_id: str
    :param job_id: ID of the Project
    :type job_id: str
    :param project_name: Name of the Project
    :type project_name: str
    ...
    """

    def __init__(self, name, account_id, job_id, project_name):
        """Constructor method"""
        self._name = name
        self._account_id = account_id
        self._job_id = job_id
        self._project_name = project_name

    @staticmethod
    def create(name, account_id, job_id, project_name):
        """Static method for obtaining DBTJobConstructor's DataSet Class
        used for getting the required infomation for Pantomath
        :param name: Name of the Job
        :type name: str
        :param account_id: ID of the Account
        :type account_id: str
        :param job_id: ID of the Project
        :type job_id: str
        :param project_name: Name of the Project
        :type project_name: str
        """
        return DBTJobConstructor(name, account_id, job_id, project_name)

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
        return str(
            DBT_ROOT_NAME_DEFAULT
            + str(self._account_id)
            + "."
            + str(self._project_name)
            + "."
            + str(self._name)
            + "."
            + str(self._job_id)
        ).lower()
