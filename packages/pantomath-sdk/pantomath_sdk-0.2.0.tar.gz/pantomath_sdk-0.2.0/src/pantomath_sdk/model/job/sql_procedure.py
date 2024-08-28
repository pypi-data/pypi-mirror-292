from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes


class SqlProcedure(Job):
    """SqlProcedure's Job Class used for getting the required infomation for Pantomath
    :param host: The Host Url
    :type host: str
    :param port: Port number
    :type port: str
    :param database: Name of the database
    :type database: str
    :param schema: Name of the Procedure's schema
    :type schema: str
    :param name: Name of the Procedure
    :type name: str
    ...
    """

    def __init__(self, host, port, database, schema, name):
        """Constructor method"""
        self._name = name
        self._schema = schema
        self._database = database
        self._port = port
        self._host = host

    @staticmethod
    def create(host, port, database, schema, name):
        """Static method for obtaining SqlProcedure's DataSet Class
        used for getting the required infomation for Pantomath
        :param host: The Host Url
        :type host: str
        :param port: Port number
        :type port: str
        :param database: Name of the database
        :type database: str
        :param schema: Name of the Procedure's schema
        :type schema: str
        :param name: Name of the Procedure
        :type name: str
        ...
        :return: SqlProcedure class object
        :rtype: SqlProcedure
        """
        return SqlProcedure(host, port, database, schema, name)

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
        return JobTypes.SQL_PROCEDURE.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return str(
            str(self._host)
            + ":"
            + str(self._port)
            + "."
            + str(self._database)
            + "."
            + str(self._schema)
            + "."
            + str(self._name)
        )
