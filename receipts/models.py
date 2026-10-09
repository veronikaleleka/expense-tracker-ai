from django.db import models

class Receipt(models.Model):
    store_name = models.CharField(max_length=200)
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    file_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.store_name} ({self.date}) - {self.total_amount}'


class Item(models.Model):
    class Category(models.TextChoices):
        FOOD = 'food', 'Food'
        DRINKS = 'drinks', 'Drinks'
        HYGIENE = 'hygiene', 'Hygiene'
        HOUSEHOLD = 'household', 'Household'
        HEALTH = 'health', 'Health'
        CLOTHING = 'clothing', 'Clothing'
        ELECTRONICS = 'electronics', 'Electronics'
        OTHER = 'other', 'Other'

    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)

    def __str__(self):
        return f'{self.name} - {self.price}'

