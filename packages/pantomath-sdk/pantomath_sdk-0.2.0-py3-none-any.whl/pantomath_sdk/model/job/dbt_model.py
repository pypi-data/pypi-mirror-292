from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class DBTModelConstructor(Job):
    """DBTModelConstructor's Job Class used for getting the required infomation for Pantomath
    :param account_id: ID of the Account
    :type account_id: str
    :param job_name: Name of the Job
    :type job_name: str
    :param package_name: Name of the Package
    :type package_name: str
    :param dbt_root_name: Name of the Root DBT
    :type dbt_root_name: str
    :param job_database_name: Job Database NAme
    :type job_database_name: str
    :param job_schema_name: Job Schema NAme
    :type job_schema_name: str
    ...
    """

    def __init__(
        self,
        account_id,
        job_name,
        package_name,
        dbt_root_name,
        job_database_name,
        job_schema_name,
    ):
        """Constructor method"""
        self._account_id = account_id
        self._job_name = job_name
        self._package_name = package_name
        self._dbt_root_name = dbt_root_name
        self._job_database_name = job_database_name
        self._job_schema_name = job_schema_name

    @staticmethod
    def create(
        account_id,
        job_name,
        package_name,
        dbt_root_name,
        job_database_name,
        job_schema_name,
    ):
        """Static method for obtaining DBTModelConstructor's DataSet Class
        used for getting the required infomation for Pantomath
        :param account_id: ID of the Account
        :type account_id: str
        :param job_name: Name of the Job
        :type job_name: str
        :param package_name: Name of the Package
        :type package_name: str
        :param dbt_root_name: Name of the Root DBT
        :type dbt_root_name: str
        :param job_database_name: Job Database NAme
        :type job_database_name: str
        :param job_schema_name: Job Schema NAme
        :type job_schema_name: str
        ...
        :return: DBTModelConstructor class object
        :rtype: DBTModelConstructor
        """
        return DBTModelConstructor(
            account_id,
            job_name,
            package_name,
            dbt_root_name,
            job_database_name,
            job_schema_name,
        )

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return self._job_name + " Model"

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return JobTypes.DBT_MODEL.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(
            str(self._dbt_root_name)
            + str(self._account_id)
            + "."
            + str(self._package_name)
            + "."
            + str(self._job_database_name)
            + "."
            + str(self._job_schema_name)
            + "."
            + str(self._job_name)
        ).lower()
