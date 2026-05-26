from rest_framework import serializers
from .models import MenuItem, MenuItemIngredientOption, Restaurant, Review


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Restaurant
        fields = '__all__'


class IngredientOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MenuItemIngredientOption
        fields = ['id', 'name', 'is_default', 'extra_price']


class MenuItemSerializer(serializers.ModelSerializer):
    restaurant         = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredient_options = IngredientOptionSerializer(many=True, read_only=True)

    class Meta:
        model  = MenuItem
        fields = [
            'id', 'restaurant', 'name', 'price',
            'diet_tags', 'mood_tags', 'ingredients',
            'ingredient_options',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, default=5)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'user_name',
            'restaurant',
            'menu_item',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'user_name', 'created_at']
