from pantomath_sdk import DataikuRecipe


def test_dataiku_model_good():
    test_node = DataikuRecipe(
        host_name="host",
        project_key="96868946864896189",
        recipe_name="DataikuRecipe Unit Test",
    )
    assert test_node.get_name() == "DataikuRecipe Unit Test"
    assert test_node.get_type() == "RECIPE"
    assert (
        test_node.get_fully_qualified_object_name()
        == "host/projects/96868946864896189/recipes/%24dataikurecipe%20unit%20test"
    )
