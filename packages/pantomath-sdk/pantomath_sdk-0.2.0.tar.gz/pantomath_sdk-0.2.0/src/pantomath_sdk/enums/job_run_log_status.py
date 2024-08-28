from aenum import Enum


class JobRunLogStatuses(Enum):
    """This class is an enum of all the JobRunLogStatuses supported by the Pantomath Python SDK."""

    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    QUEUED = "QUEUED"
    WARNING = "WARNING"

    @staticmethod
    def get_job_run_log_statuses():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(JobRunLogStatuses)[: len(JobRunLogStatuses)]

    @staticmethod
    def is_job_run_log_status(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in JobRunLogStatuses.get_job_run_log_statuses()
