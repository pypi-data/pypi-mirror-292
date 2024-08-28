from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class AWSLambda(Job):
    """AWSLambda's Job Class used for getting the required infomation for Pantomath
    :param name: Name of the lambda
    :type name: str
    ...
    """

    def __init__(self, name):
        """Constructor method"""
        self._name = name

    @staticmethod
    def create(name):
        """Static method for obtaining AWSLambda's DataSet Class
        used for getting the required infomation for Pantomath
        :param name: Name of the lambda
        :type name: str
        ...
        :return: AWSLambda class object
        :rtype: AWSLambda
        """
        return AWSLambda(name)

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
        return JobTypes.AWS_LAMBDA.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(self.get_name())
