from django.db import models

MOOD_CHOICES = [
    ('comfort',    'Comfort'),
    ('healthy',    'Healthy'),
    ('cheat',      'Cheat Meal'),
    ('spicy',      'Spicy'),
    ('late-night', 'Late Night'),
]

class Restaurant(models.Model):
    name                   = models.CharField(max_length=120)
    description            = models.TextField(blank=True, help_text="Short bio of the restaurant")
    cuisine_type           = models.CharField(max_length=100, blank=True, default="Multicuisine")
    location               = models.CharField(max_length=255, blank=True)
    image_url              = models.URLField(blank=True)
    rating                 = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    delivery_time          = models.CharField(max_length=20, default="30-40 min")
    is_active              = models.BooleanField(default=True)
    supports_customization = models.BooleanField(default=True)
    created_at             = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    restaurant  = models.ForeignKey(
        'Restaurant', on_delete=models.CASCADE, related_name='menu_items',
    )
    name        = models.CharField(max_length=100, db_index=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    diet_tags   = models.CharField(max_length=200, blank=True)
    mood_tags   = models.CharField(max_length=50, choices=MOOD_CHOICES, blank=True)
    ingredients = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MenuItemIngredientOption(models.Model):
    """Customizable ingredient options for a MenuItem (e.g. Cheese, Onion, Mushroom)."""
    menu_item   = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredient_options')
    name        = models.CharField(max_length=80)
    is_default  = models.BooleanField(default=True)
    extra_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        unique_together = ('menu_item', 'name')
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f'{self.menu_item.name} :: {self.name}'


class Review(models.Model):
    user        = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE, related_name='reviews')
    restaurant  = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='reviews')
    menu_item   = models.ForeignKey('MenuItem', on_delete=models.SET_NULL, null=True, blank=True)
    rating      = models.PositiveSmallIntegerField(default=5)  # 1-5 stars
    comment     = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name}'s review of {self.restaurant.name}"
