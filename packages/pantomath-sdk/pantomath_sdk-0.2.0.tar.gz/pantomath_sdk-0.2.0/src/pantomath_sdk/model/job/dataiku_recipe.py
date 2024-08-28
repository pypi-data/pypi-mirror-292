from pantomath_sdk.model.job.job import Job
from pantomath_sdk.enums.job_type import JobTypes
import pantomath_sdk.util as util


class DataikuRecipe(Job):
    """DataikuRecipe's Job Class used for getting the required infomation for Pantomath
    :param _host_name: Dataiku Host
    :type _host_name: str
    :param project_key: Project ID
    :type project_key: str
    :param recipe_name: Recipe name
    :type recipe_name: str
    ...
    """

    def __init__(self, host_name, project_key, recipe_name):
        """Constructor method"""
        self._host_name = host_name
        self._project_key = project_key
        self._recipe_name = recipe_name

    @staticmethod
    def create(host_name, project_key, recipe_name):
        """Static method for obtaining DataikuRecipe's DataSet Class
        used for getting the required infomation for Pantomath
        :param _host_name: Dataiku Host
        :type _host_name: str
        :param project_key: Project ID
        :type project_key: str
        :param recipe_name: Recipe name
        :type recipe_name: str
        :return: DataikuRecipe class object
        :rtype: DataikuRecipe
        """
        return DataikuRecipe(host_name, project_key, recipe_name)

    def get_name(self):
        """Returns the name of the object
        ...
        :return: the name of the object
        :rtype: str
        """
        return self._recipe_name

    def get_type(self):
        """Returns the type of the object
        ...
        :return: the type of the object
        :rtype: str
        """
        return JobTypes.RECIPE.value

    def get_fully_qualified_object_name(self):
        """Returns the Fully Qualified Name of the object
        ...
        :return: the Fully Qualified Name of the object
        :rtype: str
        """
        return util.sanitize_fully_qualified_object_name(
            util.normalize_host(
                str(
                    str(self._host_name)
                    + "/projects/"
                    + str(self._project_key)
                    + "/recipes/$"
                    + str(self._recipe_name)
                )
            )
        )
