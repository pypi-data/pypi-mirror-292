from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes
import pantomath_sdk.util as util


class AstroTask(Job):
    """AstroTask's Job Class used for getting the required infomation for Pantomath
    :param dag_name: Name of the dag
    :type dag_name: str
    :param host_name: Name of the host
    :type host_name: str
    :param name: Name of the task
    :type name: str
    ...
    """

    def __init__(self, dag_name, host_name, name):
        """Constructor method"""
        self._dag_name = dag_name
        self._host_name = host_name
        self._name = name

    @staticmethod
    def create(dag_name, host_name, name):
        """Static method for obtaining AstroTask's DataSet Class
        used for getting the required infomation for Pantomath
        :param dag_name: Name of the dag
        :type dag_name: str
        :param host_name: Name of the host
        :type host_name: str
        :param name: Name of the task
        :type name: str
        ...
        :return: AstroTask class object
        :rtype: AstroTask
        """
        return AstroTask(dag_name, host_name, name)

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
        return JobTypes.TASK.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(
            self._host_name + "/" + self._dag_name + "/" + self.get_name()
        )
