from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class SynapsePipeline(Job):
    """SynapsePipeline's Job Class used for getting the required infomation for Pantomath
    :param pipeline_id: The Pipeline ID
    :type pipeline_id: str
    :param name: Name of the Pipeline
    :type name: str
    ...
    """

    def __init__(self, pipeline_id, name):
        """Constructor method"""
        self._pipeline_id = pipeline_id
        self._name = name

    @staticmethod
    def create(pipeline_id, name):
        """Static method for obtaining SynapsePipeline's DataSet Class
        used for getting the required infomation for Pantomath
        :param pipeline_id: The Pipeline ID
        :type pipeline_id: str
        :param name: Name of the Pipeline
        :type name: str
        ...
        :return: SynapsePipeline class object
        :rtype: SynapsePipeline
        """
        return SynapsePipeline(pipeline_id, name)

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
        return JobTypes.PIPELINE.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(self._pipeline_id)
