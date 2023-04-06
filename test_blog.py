import pytest
import sqlite3
from unittest.mock import Mock
from blog import UserInputCollector, \
    UserInputChecker, QuantityTableData, RecipesDBStore, OptionalArguments, Recipe, Serve
from db_handler import DBConnection, Data
from custom_errors import MealNumberError, QuantityError, \
    MeasureError, IngredientError, UserIngredientError, UserMealError, NoIngredientsError, NoMealsError


def test_print_initial_instruction(capsys):
    UserInputCollector.print_initial_instruction()
    captured = capsys.readouterr()
    assert captured.out == "Pass the empty recipe name to exit.\n"


def test_gather_recipes(monkeypatch):
    inputs = ["Recipe 1", "This is a test recipe.", ""]
    monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
    result = UserInputCollector.gather_recipes()
    assert isinstance(result, Recipe)
    assert result.name == "Recipe 1"
    assert result.instruction == "This is a test recipe."


def test_gather_meal_numbers_valid_input(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1 3 4")
    serve = UserInputCollector.gather_meal_numbers()
    assert isinstance(serve, Serve)
    assert serve.meal_ids == [1, 3, 4]


def test_gather_meal_numbers_invalid_input_text(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "text")
    with pytest.raises(MealNumberError):
        UserInputCollector.gather_meal_numbers()


def test_gather_meal_numbers_invalid_input_no_spaces(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1234")
    with pytest.raises(MealNumberError):
        UserInputCollector.gather_meal_numbers()


def test_gather_meal_numbers_invalid_input_wrong_numbers(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1 2 5")
    with pytest.raises(MealNumberError):
        UserInputCollector.gather_meal_numbers()


def test_gather_recipe_info(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1 ml milk")
    result = UserInputCollector.gather_recipe_info()
    assert result == ("1", "ml", "milk")


def test_gather_recipe_info_no_measure(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "10 strawberry")
    result = UserInputCollector.gather_recipe_info()
    assert result == ("10", "", "strawberry")


def test_gather_recipe_info_empty_string(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "")
    result = UserInputCollector.gather_recipe_info()
    assert result is False


def test_check_quantity_valid_input():
    assert UserInputChecker.check_quantity("2") == 2


def test_check_quantity_invalid_input():
    with pytest.raises(QuantityError):
        UserInputChecker.check_quantity("text")


def test_check_measure():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()

    collector = UserInputChecker(db, 2)

    # Valid full measurement.
    result = collector.check_measure("ml")
    assert result == "ml"

    result = collector.check_measure("tbsp")
    assert result == "tbsp"

    result = collector.check_measure("")
    assert result == ""

    # Valid measurement beginning.
    result = collector.check_measure("m")
    assert result == "ml"

    result = collector.check_measure("c")
    assert result == "cup"

    # Invalid measurement.
    with pytest.raises(MeasureError):
        collector.check_measure("gallon")

    # Invalid measurement beginning.
    with pytest.raises(MeasureError):
        collector.check_measure("t")

    db.close()


def test_check_ingredient():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()

    collector = UserInputChecker(db, 2)

    # Valid full ingredient.
    result = collector.check_ingredient("milk")
    assert result == "milk"

    # Valid partial ingredient.
    result = collector.check_ingredient("blue")
    assert result == "blueberry"

    # Invalid full ingredient.
    with pytest.raises(IngredientError):
        collector.check_ingredient("flour")

    # Invalid partial ingredient.
    with pytest.raises(IngredientError):
        collector.check_ingredient("berry")

    db.close()


def test_column_to_list():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    checker = UserInputChecker(db, 1)
    result = checker._column_to_list('measures', 'measure_id')
    assert result == [1, 2, 3, 4, 5, 6, 7, 8]
    db.close()


def test_gather_measure_id():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    quantity_data = QuantityTableData(db)
    result = quantity_data.gather_measure_id("cup")
    assert result == 4
    db.close()


def test_gather_ingredient_id():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    quantity_data = QuantityTableData(db)
    result = quantity_data.gather_ingredient_id("sugar")
    assert result == 6
    db.close()


def test_create_recipe():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    recipe = Recipe("pizza marinara", "Peel tomatoes, bake dough, serve hot.")
    recipes_db_store = RecipesDBStore(db)
    recipes_db_store.create_recipe(recipe)
    result = db.conn.execute("SELECT recipe_id, recipe_name, recipe_description FROM recipes").fetchone()
    assert result[0] == 1
    assert result[1] == "pizza marinara"
    assert result[2] == "Peel tomatoes, bake dough, serve hot."
    db.close()


def test_create_serve():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    recipes_db_store = RecipesDBStore(db)
    recipes_db_store.create_serve(meal_numbers=[1, 2, 3, 4], recipe_id=1)
    result = db.conn.execute("SELECT serve_id, meal_id, recipe_id FROM serve").fetchall()
    assert result == [(1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4, 1)]
    db.close()


def test_create_quantity():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    recipes_db_store = RecipesDBStore(db)
    recipes_db_store.create_quantity(measure_id=1, ingredient_id=1, quantity=10, recipe_id=1)
    result = db.conn.execute("SELECT measure_id, ingredient_id, quantity, recipe_id FROM quantity").fetchall()
    assert result == [(1, 1, 10, 1)]
    db.close()


def test_is_input_comma_separated_commas():
    db = DBConnection(":memory:")
    optional_args = OptionalArguments(db, None)
    assert optional_args.is_input_comma_separated('milk,strawberry,blueberry') is True
    db.close()


def test_is_input_comma_separated_spaces():
    db = DBConnection(":memory:")
    optional_args = OptionalArguments(db, None)
    assert optional_args.is_input_comma_separated('milk strawberry blueberry') is False
    db.close()


def test_check_if_both_args_provided_no_ingredients():
    db = DBConnection(":memory:")
    args = Mock(ingredients=None, meals="breakfast,lunch")
    optional_args = OptionalArguments(db, args)
    with pytest.raises(NoIngredientsError):
        optional_args.check_if_both_args_provided()
    db.close()


def test_check_if_both_args_provided_no_meals():
    db = DBConnection(":memory:")
    args = Mock(ingredients="milk,blackberry", meals=None)
    optional_args = OptionalArguments(db, args)
    with pytest.raises(NoMealsError):
        optional_args.check_if_both_args_provided()
    db.close()


def test_check_user_ingredients_valid():
    db = DBConnection(":memory:")
    args = Mock(ingredients="flour,sugar,eggs")
    optional_args = OptionalArguments(db, args)
    result = optional_args.check_user_ingredients()
    assert result is True
    db.close()


def test_check_user_ingredients_invalid():
    db = DBConnection(":memory:")
    args = Mock(ingredients="flour sugar eggs")
    optional_args = OptionalArguments(db, args)
    with pytest.raises(UserIngredientError):
        optional_args.check_user_ingredients()
    db.close()


def test_check_user_meals_valid():
    db = DBConnection(":memory:")
    args = Mock(meals="breakfast,brunch,lunch,dinner")
    optional_args = OptionalArguments(db, args)
    result = optional_args.check_user_meals()
    assert result is True
    db.close()


def test_check_user_meals_invalid():
    db = DBConnection(":memory:")
    args = Mock(meals="breakfast brunch lunch dinner")
    optional_args = OptionalArguments(db, args)
    with pytest.raises(UserMealError):
        optional_args.check_user_meals()
    db.close()


def test_propose_recipes():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()
    data.seed_tables()
    # Creating sample recipes with ingredients and measures.
    db.conn.execute('''INSERT OR IGNORE INTO recipes(recipe_id, recipe_name, recipe_description)
                        VALUES (1, "pancakes", "Mix flour with milk, fry on a medium heat.")''')
    db.conn.execute('''INSERT OR IGNORE INTO recipes(recipe_id, recipe_name, recipe_description)
                        VALUES (2, "risotto", "Make broth, cook rice in a broth.")''')
    db.conn.execute('''INSERT INTO serve(serve_id, recipe_id, meal_id)
                        VALUES (1, 1, 1)''')
    db.conn.execute('''INSERT INTO serve(serve_id, recipe_id, meal_id)
                        VALUES (2, 2, 4)''')
    db.conn.execute('''INSERT INTO quantity(quantity_id, measure_id, ingredient_id, quantity, recipe_id)
                        VALUES (1, 4, 4, 1, 1)''')
    db.conn.execute('''INSERT INTO quantity(quantity_id, measure_id, ingredient_id, quantity, recipe_id)
                        VALUES (2, 4, 3, 1, 1)''')
    db.conn.execute('''INSERT INTO quantity(quantity_id, measure_id, ingredient_id, quantity, recipe_id)
                        VALUES (3, 1, 1, 100, 2)''')
    db.conn.commit()

    # When dish is available.
    args = Mock(ingredients="strawberry", meals="breakfast,brunch")
    optional_args = OptionalArguments(db, args)
    result = optional_args.propose_recipes()
    assert result == ["pancakes"]

    args = Mock(ingredients="milk", meals="breakfast,supper")
    optional_args = OptionalArguments(db, args)
    result = optional_args.propose_recipes()
    assert result == ["risotto"]

    # When dish is not available.
    args = Mock(ingredients="sugar", meals="breakfast,brunch")
    optional_args = OptionalArguments(db, args)
    result = optional_args.propose_recipes()
    assert result == []
    db.close()


def test_inform_user(capsys):
    db = DBConnection(":memory:")
    optional_args = OptionalArguments(db, None)

    # Test case 1: final_output is not empty
    optional_args.final_output = ["Recipe1", "Recipe2", "Recipe3"]
    optional_args.inform_user()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Recipes selected for you: Recipe1, Recipe2, Recipe3"

    # Test case 2: final_output is empty
    optional_args.final_output = []
    optional_args.inform_user()
    captured = capsys.readouterr()
    assert captured.out.strip() == "There are no such recipes in the database."
    db.close()
