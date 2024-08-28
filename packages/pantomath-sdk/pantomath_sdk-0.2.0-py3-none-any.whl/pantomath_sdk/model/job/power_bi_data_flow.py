from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class PowerBiDataFlow(Job):
    """PowerBiDataFlow's Job Class used for getting the required infomation for Pantomath
    :param group_id: The Group ID
    :type group_id: str
    :param object_id: The Object ID
    :type object_id: str
    :param name: Name of the Data  Flow
    :type name: str
    ...
    """

    def __init__(self, group_id, object_id, name):
        """Constructor method"""
        self._name = name
        self._object_id = object_id
        self._groupId = group_id

    @staticmethod
    def create(group_id, object_id, name):
        """Static method for obtaining PowerBiDataFlow's DataSet Class
        used for getting the required infomation for Pantomath
        :param group_id: The Group ID
        :type group_id: str
        :param object_id: The Object ID
        :type object_id: str
        :param name: Name of the Data  Flow
        :type name: str
        ...
        :return: PowerBiDataFlow class object
        :rtype: PowerBiDataFlow
        """
        return PowerBiDataFlow(group_id, object_id, name)

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
        return JobTypes.POWER_BI_DATAFLOW.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(
            "app.powerbi.com/groups/" + self._groupId + "/dataflows/" + self._object_id
        ).lower()
