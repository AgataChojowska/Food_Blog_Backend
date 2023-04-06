import argparse
from food_blog.db_handler import Data
from food_blog.blog import DBConnection, UserInputCollector, \
    UserInputChecker, QuantityTableData, RecipesDBStore, OptionalArguments
from food_blog.custom_errors import MealNumberError, QuantityError, UserIngredientError, UserMealError, NoIngredientsError, \
    NoMealsError

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("db")
    parser.add_argument("-i1", "--ingredients", help="Provide ingredients separated by a comma.")
    parser.add_argument("-m1", "--meals", help="Provide meals separated by a comma.")
    args = parser.parse_args()

    db = DBConnection(args.db)
    db.turn_on_foreign_keys()
    data = Data(db)
    data.create_tables()
    data.seed_tables()

    try:
        optional_args = OptionalArguments(db, args)
        optional_args.check_if_both_args_provided()
    except NoIngredientsError as e:
        print(e)
        quit()
    except NoMealsError as e:
        print(e)
        quit()

    if args.ingredients is not None and args.meals is not None:
        optional_args = OptionalArguments(db, args)
        try:
            optional_args.check_user_ingredients()
            optional_args.check_user_meals()
        except UserIngredientError as e:
            print(e)
            exit()
        except UserMealError as e:
            print(e)
            exit()
        optional_args.propose_recipes()
        optional_args.inform_user()
        exit()

    UserInputCollector.print_initial_instruction()
    while True:
        user_input = UserInputCollector()
        recipes_db_store = RecipesDBStore(db)
        quality_table_data = QuantityTableData(db)

        recipe_obj = user_input.gather_recipes()
        try:
            serve_obj = user_input.gather_meal_numbers()
        except MealNumberError as e:
            print(e)
            continue
        recipe_id = recipes_db_store.create_recipe(recipe_obj)
        recipes_db_store.create_serve(serve_obj.meal_ids, recipe_id)

        input_checker = UserInputChecker(db, recipe_id)
        try:
            input_checker.execute_checks()
        except QuantityError as e:
            print(e)
            continue

