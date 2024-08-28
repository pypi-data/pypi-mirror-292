from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class S3Bucket(DataSet):
    """S3Bucket's DataSet Class used for getting the required infomation for Pantomath
    :param s3_bucket: The name of the s3_bucket
    :type s3_bucket: str
    ...
    """

    def __init__(self, s3_bucket):
        """Constructor method"""
        self._s3_bucket = s3_bucket

    @staticmethod
    def create(s3_bucket):
        """Static method for obtaining S3Bucket's DataSet Class
        used for getting the required infomation for Pantomath
        :param s3_bucket: The name of the s3_bucket
        :type s3_bucket: str
        ...
        :return: S3Bucket class object
        :rtype: S3Bucket
        """
        return S3Bucket(s3_bucket)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return self._s3_bucket

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return DataSetTypes.S3_BUCKET.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return self._s3_bucket
