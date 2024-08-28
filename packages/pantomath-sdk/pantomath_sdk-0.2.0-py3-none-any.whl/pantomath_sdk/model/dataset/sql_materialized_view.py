from pantomath_sdk.model.dataset.dataset import DataSet
from pantomath_sdk.enums.dataset_type import DataSetTypes


class SqlMaterializedView(DataSet):
    """SqlMaterializedView's DataSet Class used for getting the required infomation for Pantomath
    :param host: The SQL Host Url
    :type host: str
    :param port: Port number
    :type port: str
    :param database: Name of the database
    :type database: str
    :param schema: Name of the view's schema
    :type schema: str
    :param name: Name of the View
    :type name: str
    ...
    """

    def __init__(self, host, port, database, schema, name):
        """Constructor method"""
        self._host = host
        self._port = port
        self._database = database
        self._schema = schema
        self._name = name

    @staticmethod
    def create(host, port, database, schema, name):
        """Static method for obtaining SqlMaterializedView's DataSet Class
        used for getting the required infomation for Pantomath
        :param host: The SQL Host Url
        :type host: str
        :param port: Port number
        :type port: str
        :param database: Name of the database
        :type database: str
        :param schema: Name of the view's schema
        :type schema: str
        :param name: Name of the View
        :type name: str
        ...
        :return: SqlMaterializedView class object
        :rtype: SqlMaterializedView
        """
        return SqlMaterializedView(host, port, database, schema, name)

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
        return DataSetTypes.SQL_MATERIALIZED_VIEW.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return (
            self._host
            + ":"
            + str(self._port)
            + "."
            + self._database
            + "."
            + self._schema
            + "."
            + self._name
        )
