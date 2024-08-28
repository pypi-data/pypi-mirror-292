from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes
import pantomath_sdk.util as util


class TableauExtractRefreshTask(Job):
    """TableauExtractRefreshTask's Job Class used for getting the required infomation for Pantomath
    :param host: Host URL
    :type host: str
    :param site_id: ID of the site
    :type site_id: str
    :param refresh_id: The Refresh ID
    :type refresh_id: str
    :param name: Name of the Refresh
    :type name: str
    ...
    """

    def __init__(self, host, site_id, refresh_id, name):
        """Constructor method"""
        self._name = name
        self._host = host
        self._site_id = site_id
        self._refresh_id = refresh_id

    @staticmethod
    def create(host, site_id, refresh_id, name):
        """Static method for obtaining TableauExtractRefreshTask's DataSet Class
        used for getting the required infomation for Pantomath
        :param host: Host URL
        :type host: str
        :param site_id: ID of the site
        :type site_id: str
        :param refresh_id: The Refresh ID
        :type refresh_id: str
        :param name: Name of the Refresh
        :type name: str
        ...
        :return: TableauExtractRefreshTask class object
        :rtype: TableauExtractRefreshTask
        """
        return TableauExtractRefreshTask(host, site_id, refresh_id, name)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return util.sanitize_tableau_string(self._name)

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return JobTypes.TABLEAU_EXTRACT_REFRESH_TASK.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(
            util.normalize_host(self._host)
            + "/site/"
            + self._site_id
            + "/task/"
            + self._refresh_id
        ).lower()
