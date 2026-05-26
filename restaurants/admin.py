from django.contrib import admin
from .models import MenuItem, Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'supports_customization', 'created_at')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'restaurant', 'diet_tags', 'mood_tags')
