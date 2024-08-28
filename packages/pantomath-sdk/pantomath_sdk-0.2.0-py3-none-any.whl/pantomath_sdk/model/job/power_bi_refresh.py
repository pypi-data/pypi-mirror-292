from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class PowerBIRefresh(Job):
    """PowerBIRefresh's Job Class used for getting the required infomation for Pantomath
    :param dataset_id: The dataset ID
    :type dataset_id: str
    :param refresh_schedule_context: Name of the refresh_schedule_context
    :type refresh_schedule_context: str
    :param name: Name of the activity
    :type name: str
    ...
    """

    def __init__(self, dataset_id, refresh_schedule_context, name):
        """Constructor method"""
        self._name = name
        self._refresh_schedule_context = refresh_schedule_context
        self._dataset_id = dataset_id

    @staticmethod
    def create(dataset_id, refresh_schedule_context, name):
        """Static method for obtaining PowerBIRefresh's DataSet Class
        used for getting the required infomation for Pantomath
        :param dataset_id: The dataset ID
        :type dataset_id: str
        :param refresh_schedule_context: Name of the refresh_schedule_context
        :type refresh_schedule_context: str
        :param name: Name of the activity
        :type name: str
        ...
        :return: PowerBIRefresh class object
        :rtype: PowerBIRefresh
        """
        return PowerBIRefresh(dataset_id, refresh_schedule_context, name)

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
        return JobTypes.POWER_BI_REFRESH.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return (
            str(
                self._refresh_schedule_context
                + "/"
                + self._dataset_id
                + "/"
                + self._name
            ).replace(" ", "_")
        ).lower()
