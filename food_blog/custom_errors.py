class MealNumberError(Exception):
    def __init__(self):
        self.message = "Provide one number or multiple numbers from range 1-4 separated by single spaces."
        super().__init__(self.message)


class QuantityError(Exception):
    def __init__(self):
        self.message = "Quantity must be a number."
        super().__init__(self.message)


class MeasureError(Exception):
    def __init__(self):
        self.message = "The measure is not conclusive!"
        super().__init__(self.message)


class IngredientError(Exception):
    def __init__(self):
        self.message = "The ingredient is not conclusive!"
        super().__init__(self.message)


class UserIngredientError(Exception):
    def __init__(self):
        self.message = "Provide ingredients separated by a comma."
        super().__init__(self.message)


class UserMealError(Exception):
    def __init__(self):
        self.message = "Provide meals separated by a comma."
        super().__init__(self.message)


class NoIngredientsError(Exception):
    def __init__(self):
        self.message = "Provide ingredients."
        super().__init__(self.message)


class NoMealsError(Exception):
    def __init__(self):
        self.message = "Provide meals."
        super().__init__(self.message)
