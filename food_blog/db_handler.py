import sqlite3


class DBConnection:

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)

    def turn_on_foreign_keys(self):
        self.conn.execute('''PRAGMA foreign_keys = ON''')

    def turn_off_foreign_keys(self):
        self.conn.execute('''PRAGMA foreign_keys = OFF''')

    def close(self):
        self.conn.close()


class Data:

    def __init__(self, db: DBConnection):
        self.db = db

    def create_tables(self):
        c = self.db.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS meals(
            meal_id INTEGER PRIMARY KEY,
            meal_name TEXT NOT NULL UNIQUE
            )''')

        c.execute('''CREATE TABLE IF NOT EXISTS ingredients(
            ingredient_id INTEGER PRIMARY KEY,
            ingredient_name TEXT NOT NULL UNIQUE)
            ''')

        c.execute('''CREATE TABLE IF NOT EXISTS measures(
            measure_id INTEGER PRIMARY KEY,
            measure_name TEXT UNIQUE)
            ''')

        c.execute('''CREATE TABLE IF NOT EXISTS recipes(
            recipe_id INTEGER PRIMARY KEY,
            recipe_name TEXT NOT NULL,
            recipe_description TEXT)
            ''')

        c.execute('''CREATE TABLE IF NOT EXISTS serve (
            serve_id INTEGER PRIMARY KEY,
            recipe_id INTEGER NOT NULL,
            meal_id INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
            FOREIGN KEY (meal_id) REFERENCES meals(meal_id))
            ''')

        c.execute('''CREATE TABLE IF NOT EXISTS quantity (
            quantity_id INTEGER PRIMARY KEY,
            measure_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            FOREIGN KEY (measure_id) REFERENCES measures(measure_id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id))         
            ''')
        self.db.conn.commit()

    def seed_tables(self):
        c = self.db.conn.cursor()
        c.execute('''INSERT OR IGNORE INTO meals(meal_name) 
            VALUES ("breakfast"), ("brunch"), ("lunch"), ("supper")
            ''')
        self.db.conn.commit()

        c.execute('''INSERT OR IGNORE INTO ingredients(ingredient_name)
                    VALUES ("milk"), ("cacao"), ("strawberry"), ("blueberry"), ("blackberry"), ("sugar")
                    ''')
        self.db.conn.commit()

        c.execute('''INSERT OR IGNORE INTO measures(measure_name)
                    VALUES ("ml"), ("g"), ("l"), ("cup"), ("tbsp"), ("tsp"), ("dsp"), ("")
                    ''')
        self.db.conn.commit()

