from django.db import models

# Create your models here.

class Ingredient(models.Model):
    """
    Represents a single ingredient in the restaurant's inventory.
    """
    name = models.CharField(max_length=100, unique=True)
    quantity_available = models.FloatField(default=0.0)
    unit = models.CharField(max_length=20) # E.g., "kg", "lbs", "g", "each"
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.quantity_available} {self.unit})"

class MenuItem(models.Model):
    """
    Represents a single item on the restaurant's menu.
    """
    title = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.title} - ${self.price}"

    def is_available(self):
        """
        Checks if there are enough ingredients in inventory to make this menu item.
        """
        return all(
            req.ingredient.quantity_available >= req.quantity_required
            for req in self.reciperequirement_set.all()
        )

class RecipeRequirement(models.Model):
    """
    Links MenuItem and Ingredient to define a recipe.
    E.g., "Margherita Pizza requires 0.2 kg of Flour"
    """
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.FloatField()

    def __str__(self):
        return f"{self.menu_item.title} requires {self.quantity_required} {self.ingredient.unit} of {self.ingredient.name}"

class Purchase(models.Model):
    """
    Represents a log of a single customer purchase.
    """
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase of {self.menu_item.title} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"