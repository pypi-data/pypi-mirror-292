from aenum import Enum


class JobDidNotRunAtMethods(Enum):
    """This class is an enum of all the JobDidNotRunAtMethods
    supported by the Pantomath Python SDK."""

    TRIGGER_TYPE = "TRIGGER_TYPE"
    NEXT_RUN_AT = "NEXT_RUN_AT"

    @staticmethod
    def get_job_did_not_run_at_method():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(JobDidNotRunAtMethods)[: len(JobDidNotRunAtMethods)]

    @staticmethod
    def is_job_did_not_run_at_method(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in JobDidNotRunAtMethods.get_job_did_not_run_at_method()
