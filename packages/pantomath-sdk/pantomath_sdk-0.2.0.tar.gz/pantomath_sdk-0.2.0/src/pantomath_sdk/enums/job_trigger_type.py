from aenum import Enum


class JobTriggerTypes(Enum):
    """This class is an enum of all the JobTriggerTypes supported by the Pantomath Python SDK."""

    SCHEDULE = "SCHEDULE"
    MANUAL = "MANUAL"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def get_job_trigger_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(JobTriggerTypes)[: len(JobTriggerTypes)]

    @staticmethod
    def is_job_trigger_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in JobTriggerTypes.get_job_trigger_types()
