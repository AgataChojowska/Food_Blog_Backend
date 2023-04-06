import pytest
import sqlite3
from db_handler import DBConnection, Data


def test_turn_on_foreign_keys():
    db_name = ":memory:"
    db = DBConnection(db_name)
    db.turn_on_foreign_keys()
    c = db.conn.cursor()
    c.execute('''PRAGMA foreign_keys''')
    result = c.fetchone()
    assert result[0] == 1
    db.close()


def test_turn_off_foreign_keys():
    db_name = ":memory:"
    db = DBConnection(db_name)
    db.turn_off_foreign_keys()
    c = db.conn.cursor()
    c.execute('''PRAGMA foreign_keys''')
    result = c.fetchone()
    assert result[0] == 0
    db.close()


def test_create_tables():
    db_name = ":memory:"
    db = DBConnection(db_name)
    data = Data(db)
    data.create_tables()

    # Check if the tables have been created
    cursor = db.conn.cursor()
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' ORDER BY name''')
    result = cursor.fetchall()
    assert result == [('ingredients',), ('meals',), ('measures',), ('quantity',), ('recipes',), ('serve',)]

    # Check if the columns in the tables have been created correctly
    cursor.execute('''PRAGMA table_info('meals')''')
    result = cursor.fetchall()
    assert result == [(0, 'meal_id', 'INTEGER', 0, None, 1), (1, 'meal_name', 'TEXT', 1, None, 0)]

    cursor.execute('''PRAGMA table_info('ingredients')''')
    result = cursor.fetchall()
    assert result == [(0, 'ingredient_id', 'INTEGER', 0, None, 1), (1, 'ingredient_name', 'TEXT', 1, None, 0)]

    cursor.execute('''PRAGMA table_info('measures')''')
    result = cursor.fetchall()
    assert result == [(0, 'measure_id', 'INTEGER', 0, None, 1), (1, 'measure_name', 'TEXT', 0, None, 0)]

    cursor.execute('''PRAGMA table_info('recipes')''')
    result = cursor.fetchall()
    assert result == [(0, 'recipe_id', 'INTEGER', 0, None, 1), (1, 'recipe_name', 'TEXT', 1, None, 0),
                      (2, 'recipe_description', 'TEXT', 0, None, 0)]

    cursor.execute('''PRAGMA table_info('serve')''')
    result = cursor.fetchall()
    assert result == [(0, 'serve_id', 'INTEGER', 0, None, 1), (1, 'recipe_id', 'INTEGER', 1, None, 0),
                      (2, 'meal_id', 'INTEGER', 1, None, 0)]

    cursor.execute('''PRAGMA table_info('quantity')''')
    result = cursor.fetchall()
    assert result == [(0, 'quantity_id', 'INTEGER', 0, None, 1), (1, 'measure_id', 'INTEGER', 1, None, 0),
                      (2, 'ingredient_id', 'INTEGER', 1, None, 0), (3, 'quantity', 'INTEGER', 1, None, 0),
                      (4, 'recipe_id', 'INTEGER', 1, None, 0)]

    db.close()


def test_seed_tables():
    db = DBConnection(":memory:")
    data = Data(db)
    data.create_tables()

    data.seed_tables()

    meals = db.conn.execute("SELECT meal_name FROM meals").fetchall()
    assert len(meals) == 4
    assert ("breakfast",) in meals
    assert ("brunch",) in meals
    assert ("lunch",) in meals
    assert ("supper",) in meals

    ingredients = db.conn.execute("SELECT ingredient_name FROM ingredients").fetchall()
    assert len(ingredients) == 6
    assert ("milk",) in ingredients
    assert ("cacao",) in ingredients
    assert ("strawberry",) in ingredients
    assert ("blueberry",) in ingredients
    assert ("blackberry",) in ingredients
    assert ("sugar",) in ingredients

    measures = db.conn.execute("SELECT measure_name FROM measures").fetchall()
    assert len(measures) == 8
    assert ("ml",) in measures
    assert ("g",) in measures
    assert ("l",) in measures
    assert ("cup",) in measures
    assert ("tbsp",) in measures
    assert ("tsp",) in measures
    assert ("dsp",) in measures
    assert ("",) in measures

    db.close()
