# Food Blog Backend

A simple backend for food blog. Database contains several tables with foreign keys. Program has 2 functionalities:
1. User can input new recipes with ingredients and instructions via command line. User input is saved to a several tables in a database, that are connected via foreign keys.  
2. User can provide ingredients available to him via command line and the program will propose most suitable recipes from the database.

Objectives:
1. Create a database. Pass the name of the database to the script as an argument.
2. Create a table named meals with two columns: meal_id of an integer type with the primary key attribute, and meal_name of a text type and with the unique and not null attribute.
3. Create a table named ingredients with two columns: ingredient_id of an integer type with the primary key attribute and ingredient_name of a text type with the unique and not null attribute. Multi-word ingredients are out of scope, you don't need to implement their support in your script.
4. Create a table named measures with two columns: measure_id of an integer type with the primary key attribute, and measure_name of a text type with the unique attribute.
5. Populate the tables.
data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
6. Create a table named recipes with three columns: recipe_id of an integer type with the primary key attribute, recipe_name of a text type with the not-null attribute, and recipe_description of a text type.
7. Prepare a simple system that allows you to populate this table. Ask for the recipe name and the cooking directions, and insert the data into the table.
8. When a zero-length string is entered for the recipe name the script should terminate.
9. Create a table named serve with three columns: serve_id of an INTEGER type with the PRIMARY KEY attribute, and recipe_id and meal_id, both of INTEGER type with the NOT NULL attribute.
10. Assign the recipe_id and meal_id as Foreign Keys to the following tables: recipes (the recipe_id column) and meals (the meal_id column).
11. Once a user has entered a dish name and a recipe description print all available meals with their primary key numbers.
12. Ask a user when this dish can be served. Users should input numbers separated by a space.
13. Input values to the serve table. If the user has selected three meals when the dish can be served, there should be three new entries in the serve table.
14. Create a table named quantity with five columns: quantity_id of an INTEGER type with the PRIMARY KEY attribute, and four other columns: measure_id, ingredient_id, quantity and recipe_id . They should be of an INTEGER type with the NOT NULL attribute.
15. Assign the following columns measure_id, ingredient_id and recipe_id as Foreign Keys to the following tables (columns): measures (measure_id), ingredients (ingredient_id), and recipes (recipe_id)
16. After asking a user about certain mealtime, make a loop that will gather information about the ingredients. The ingredients should be entered in the following format: quantity measure ingredient.
17. Pressing <Enter> should finish the information gathering.
18. The measure parameter should start with a string provided by a user. If there is more than one measure that starts with the provided string, ask the user again. For example tbs and tbsp both start with the t. So the 1 t sugar entry should not pass.
19. Mind that the measures table contains an entry where the measure_name is empty string, it means, that the measure could be not provided. In this case, use this entry to relate tables. For example, 1 strawberry should have a measure_key from the entry with an empty name.
20. The ingredient parameter should contain strings provided by a user. If there is more than one ingredient that contains the provided string, ask the user again. For example strawberry and blueberry both contain berry as part of the string. So the 10 kg berry entry should not pass.
