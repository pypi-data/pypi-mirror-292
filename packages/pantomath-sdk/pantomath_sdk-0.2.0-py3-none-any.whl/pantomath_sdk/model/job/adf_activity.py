from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes
import pantomath_sdk.util as util


class ADFActivity(Job):
    """ADFActivity's Job Class used for getting the required infomation for Pantomath
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
        """Static method for obtaining ADFActivity's DataSet Class
        used for getting the required infomation for Pantomath
        :param pipeline_id: The Pipeline ID
        :type pipeline_id: str
        :param name: Name of the activity
        :type name: str
        ...
        :return: ADFActivity class object
        :rtype: ADFActivity
        """
        return ADFActivity(pipeline_id, name)

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
        return JobTypes.ADF_ACTIVITY.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(
            str(str(self._pipeline_id) + "/activities/" + str(self._name))
        )
