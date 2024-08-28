import uuid
from pantomath_sdk.model.job.job import Job
import datetime


class JobRunLog(Job):
    """JobRunLog's Job Class used for getting the required infomation for Pantomath
    :param job_run: Job Run to be logged
    :type job_run: JobRun
    :param status: Status of the Job Run
    :type status: JobRunLogStatuses
    :param message: Message for the log, defaults to empty string
    :type message: str
    :param records_effected: Number of records effected, defaults to None
    :type records_effected: number
    :param timestamp: Timestamp of the time the job ran, defaults to current UTC time
    :type timestamp: datetime
    ...
    """

    def __init__(
        self,
        job_run,
        status,
        message="",
        records_effected=None,
        timestamp=None,
    ):
        """Constructor method"""
        self._unique_id = uuid.uuid4()
        self._job_run = job_run
        self._status = status
        self._message = message
        self._records_effected = records_effected
        self._timestamp = datetime.datetime.utcnow() if timestamp is None else timestamp

    @staticmethod
    def create(job_run, status, message, records_effected, timestamp):
        """Static method for obtaining JobRunLog's DataSet Class
         used for getting the required infomation for Pantomath
        :param job_run: Job Run to be logged
        :type job_run: JobRun
        :param status: Status of the Job Run
        :type status: JobRunLogStatuses
        :param message: Message for the log, defaults to empty string
        :type message: str
        :param records_effected: Number of records effected, defaults to None
        :type records_effected: number
        :param timestamp: Timestamp of the time the job ran, defaults to current UTC time
        :type timestamp: datetime
        ...
        :return: JobRunLog class object
        :rtype: JobRunLog
        """
        return JobRunLog(job_run, status, message, records_effected, timestamp)

    def get_unique_id(self):
        """Returns the UUID of the log
        ...
        :return: Returns the UUID of the log
        :rtype: str
        """
        return self._unique_id

    def get_job_run(self):
        """Returns the logs JobRun
        ...
        :return: Returns the logs JobRun
        :rtype: JobRun
        """
        return self._job_run

    def get_status(self):
        """Returns the status of the log
        ...
        :return: Returns the status of the log
        :rtype: str
        """
        return self._status

    def get_message(self):
        """Returns the message of the log
        ...
        :return: Returns the message of the log
        :rtype: str
        """
        return self._message if self._message else None

    def get_records_effected(self):
        """Returns the number of records effected in the log
        ...
        :return: Returns the number of records effected in the log
        :rtype: number, None
        """
        return int(self._records_effected) if self._records_effected else None

    def get_timestamp(self):
        """Returns the timestamp of the log
        ...
        :return: Returns the timestamp of the log
        :rtype: datetime
        """
        return self._timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
