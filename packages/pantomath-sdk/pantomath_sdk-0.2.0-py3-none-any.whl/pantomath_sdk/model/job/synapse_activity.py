from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class SynapseActivity(Job):
    """SynapseActivity's Job Class used for getting the required infomation for Pantomath
    :param pipeline_id: The Pipeline ID
    :type pipeline_id: str
    :param name: Name of the activity
    :type name: str
    ...
    """

    def __init__(self, pipeline_id, name):
        """Constructor method"""
        self._pipeline_id = pipeline_id
        self._name = name

    @staticmethod
    def create(pipeline_id, name):
        """Static method for obtaining SynapseActivity's DataSet Class
        used for getting the required infomation for Pantomath
        :param pipeline_id: The Pipeline ID
        :type pipeline_id: str
        :param name: Name of the activity
        :type name: str
        ...
        :return: SynapseActivity class object
        :rtype: SynapseActivity
        """
        return SynapseActivity(pipeline_id, name)

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
        return JobTypes.ACTIVITY.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(self._pipeline_id + "/activities/" + self._name).lower()
