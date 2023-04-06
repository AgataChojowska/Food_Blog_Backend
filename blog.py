import sqlite3
from typing import List
import re
from db_handler import DBConnection
from custom_errors import MealNumberError, QuantityError, MeasureError, IngredientError, UserIngredientError, \
    UserMealError, NoIngredientsError, NoMealsError


class UserInputCollector:

    @staticmethod
    def print_initial_instruction():
        print("Pass the empty recipe name to exit.")

    @staticmethod
    def gather_recipes():
        name = input("Recipe name:")
        if name == "":
            exit()
        instruction = input("Recipe description:")
        if instruction == "":
            exit()
        recipe = Recipe(name, instruction)
        return recipe

    @staticmethod
    def gather_meal_numbers():
        allowed_options = [1, 2, 3, 4]
        print("1) breakfast 2) brunch 3) lunch 4) supper\nEnter proposed meals separated by a space:")
        meal_ids = input("When the dish can be served:")
        try:
            meal_numbers = [int(x) for x in meal_ids.split(" ")]
        except ValueError:
            raise MealNumberError
        for x in meal_numbers:
            if x not in allowed_options:
                raise MealNumberError
        serve = Serve(meal_numbers)
        return serve

    @staticmethod
    def gather_recipe_info():
        recipe_info = input("Input quantity of ingredient <press enter to stop>:")
        if recipe_info == "":
            return False
        quantity = recipe_info.split(" ")[0]
        if len(recipe_info.split(" ")) < 3:
            measure = ""
            ingredient = " ".join(recipe_info.split(" ")[1:])
        else:
            measure = recipe_info.split(" ")[1]
            ingredient = " ".join(recipe_info.split(" ")[2:])
        return quantity, measure, ingredient


class UserInputChecker:

    def __init__(self, db: DBConnection, recipe_id):
        self.db = db
        self.recipes_db_store = RecipesDBStore(self.db)
        self.quantity_table_data = QuantityTableData(self.db)
        self.recipe_id = recipe_id

        self.all_measures = self._get_all_measures()
        self.all_ingredients = self._get_all_ingredients()

    @staticmethod
    def check_quantity(user_quantity):
        try:
            user_quantity = int(user_quantity)
        except ValueError:
            raise QuantityError
        return user_quantity

    def check_measure(self, user_measure):
        temp_measure = [m for m in self.all_measures if m.startswith(user_measure)]
        if user_measure == "":
            return user_measure
        if len(temp_measure) > 1 or temp_measure == []:
            raise MeasureError
        return temp_measure[0]

    def check_ingredient(self, user_ingredient):
        temp_ing = [ing for ing in self.all_ingredients if user_ingredient in ing]
        if len(temp_ing) > 1 or temp_ing == []:
            raise IngredientError
        return temp_ing[0]

    def execute_checks(self):
        while True:
            whole_input = UserInputCollector.gather_recipe_info()
            if whole_input is False:
                break
            try:
                quantity = self.check_quantity(whole_input[0])
                measure_name = self.check_measure(whole_input[1])
                ingredient_name = self.check_ingredient(whole_input[2])
            except QuantityError as q:
                print(q)
                continue
            except MeasureError as m:
                print(m)
                continue
            except IngredientError as i:
                print(i)
                continue
            measure_id = self.quantity_table_data.gather_measure_id(measure_name)
            ingredient_id = self.quantity_table_data.gather_ingredient_id(ingredient_name)
            self.recipes_db_store.create_quantity(measure_id, ingredient_id, quantity, self.recipe_id)

    def _get_all_measures(self):
        return self._column_to_list('measures', 'measure_name')

    def _get_all_ingredients(self):
        return self._column_to_list('ingredients', 'ingredient_name')

    def _column_to_list(self, table, column_name):
        c = self.db.conn.cursor()
        result = c.execute(f"SELECT {column_name} FROM {table}")
        return [x[0] for x in result.fetchall()]


class Recipe:

    def __init__(self, name, instruction):
        self.name = name
        self.instruction = instruction


class Serve:

    def __init__(self, meal_ids: List):
        self.meal_ids = meal_ids


class QuantityTableData:

    def __init__(self, db: DBConnection):
        self.db = db
        self.c = db.conn.cursor()

    def gather_measure_id(self, measure):
        measure_result = self.c.execute(f"SELECT measure_id FROM measures WHERE measure_name IN (?)", [measure])
        measure_id = measure_result.fetchone()[0]
        return measure_id

    def gather_ingredient_id(self, ingredient):
        ingredient_result = self.c.execute(
            f"SELECT ingredient_id FROM ingredients WHERE ingredient_name = (?)", [ingredient])
        ingredient_id = ingredient_result.fetchone()[0]
        return ingredient_id


class RecipesDBStore:

    def __init__(self, db: DBConnection):
        self.db = db
        self.c = db.conn.cursor()

    def create_recipe(self, recipe_object: Recipe):
        result = self.c.execute(
            f"INSERT INTO recipes(recipe_name, recipe_description) VALUES (?,?)",
            [recipe_object.name, recipe_object.instruction])
        self.db.conn.commit()
        return result.lastrowid

    def create_serve(self, meal_numbers: List, recipe_id):
        for number in meal_numbers:
            self.c.execute(
                f"INSERT INTO serve(meal_id, recipe_id) VALUES (?,?)",
                [number, recipe_id])
        self.db.conn.commit()

    def create_quantity(self, measure_id, ingredient_id, quantity, recipe_id):
        c = self.db.conn.cursor()
        c.execute(
            f"INSERT INTO quantity(measure_id, ingredient_id, quantity, recipe_id) "
            f"VALUES (?,?,?,?)", [measure_id, ingredient_id, quantity, recipe_id])
        self.db.conn.commit()


class OptionalArguments:

    def __init__(self, db, args):
        self.db = db
        self.c = db.conn.cursor()
        self.args = args
        self.final_output = []

    @staticmethod
    def is_input_comma_separated(input_string):
        pattern = re.compile(r"^(\w+)(,\s*\w+)*$")
        if pattern.match(input_string) is None:
            return False
        return True

    def check_if_both_args_provided(self):
        if self.args.ingredients is None and self.args.meals is not None:
            raise NoIngredientsError
        if self.args.ingredients is not None and self.args.meals is None:
            raise NoMealsError

    def check_user_ingredients(self):
        if self.is_input_comma_separated(self.args.ingredients) is False:
            raise UserIngredientError
        return True

    def check_user_meals(self):
        if self.is_input_comma_separated(self.args.meals) is False:
            raise UserMealError
        return True

    def propose_recipes(self):
        ing_bindings = ["?" for _ in self.args.ingredients.split(',')]
        meal_bindings = ["?" for _ in self.args.meals.split(',')]
        meals_ing = self.args.ingredients.split(',') + self.args.meals.split(',')

        proposed_recipes = self.c.execute(f"""SELECT DISTINCT r.recipe_id, recipe_name,
                                          COUNT(ingredient_name) AS number_of_ingredients
                                          FROM recipes r
                                          JOIN quantity q
                                          ON r.recipe_id = q.recipe_id
                                          JOIN ingredients i
                                          ON i.ingredient_id = q.ingredient_id
                                          JOIN serve s
                                          ON s.recipe_id = r.recipe_id
                                          JOIN meals m
                                          ON m.meal_id = s.meal_id
                                          WHERE ingredient_name IN ({', '.join(ing_bindings)})
                                          AND meal_name IN ({', '.join(meal_bindings)})
                                          GROUP BY r.recipe_id, recipe_name
                                          HAVING number_of_ingredients = {len(ing_bindings)}""",
                                          meals_ing)

        fetched = proposed_recipes.fetchall()
        output_recipes = [x[1] for x in fetched]
        self.final_output.extend(output_recipes)
        return output_recipes

    def inform_user(self):
        if len(self.final_output) > 0:
            print(f"Recipes selected for you: {', '.join(self.final_output)}")
        else:
            print("There are no such recipes in the database.")