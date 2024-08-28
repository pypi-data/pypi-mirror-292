from aenum import Enum


class DataVolumeObjectTypes(Enum):
    """This class is an enum of all the DataVolumes supported by the Pantomath Python SDK."""

    SQL_TABLE = "SQL_TABLE"

    @staticmethod
    def get_data_volume_object_types():
        """Get a list of all the enum values
        ...
        :return: list of all the enum values
        :rtype: list of strings
        """
        return dir(DataVolumeObjectTypes)[: len(DataVolumeObjectTypes)]

    @staticmethod
    def is_data_volume_object_type(input):
        """Validates if the unput is part of the enum
        :param input: string to check if part of enum
        :type input: str
        ...
        :return: True if in enum else False
        :rtype: Boolean
        """
        return input in DataVolumeObjectTypes.get_data_volume_object_types()
