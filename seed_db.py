import os
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

from restaurants.models import Restaurant, MenuItem, MenuItemIngredientOption, Review
from users.models import UserProfile

def seed_data():
    print("Cleaning old data...")
    Review.objects.all().delete()
    MenuItem.objects.all().delete()
    Restaurant.objects.all().delete()

    User = get_user_model()
    django_user = User.objects.filter(email__iexact='test@example.com').first()
    if not django_user:
        django_user = User(username='test@example.com', email='test@example.com')
        django_user.set_unusable_password()
        django_user.save()

    user = UserProfile.objects.filter(user=django_user).first()
    if not user:
        user = UserProfile.objects.create(
            user=django_user,
            name="Test User",
            email="test@example.com",
            diet_preferences="vegetarian",
        )

    restaurants_data = [
        {
            "name": "The Green Bowl", 
            "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
            "description": "Healthy, organic, and locally sourced salads and bowls.",
            "cuisine_type": "Healthy / Vegan",
            "location": "Indiranagar, Bangalore",
            "rating": 4.5,
            "delivery_time": "20-30 min"
        },
        {
            "name": "Spice Route", 
            "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe",
            "description": "Authentic Indian flavors from across the country.",
            "cuisine_type": "North Indian",
            "location": "Koramangala, Bangalore",
            "rating": 4.2,
            "delivery_time": "35-45 min"
        },
        {
            "name": "Burger Haven", 
            "image_url": "https://images.unsplash.com/photo-1571091718767-18b5b1457add",
            "description": "The best messy burgers in town.",
            "cuisine_type": "American",
            "location": "HSR Layout, Bangalore",
            "rating": 4.0,
            "delivery_time": "15-25 min"
        },
        {
            "name": "Sushi Zen", 
            "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c",
            "description": "Fresh, premium sushi and Japanese delights.",
            "cuisine_type": "Japanese",
            "location": "Lavelle Road, Bangalore",
            "rating": 4.8,
            "delivery_time": "40-50 min"
        },
        {
            "name": "Pasta Paradiso", 
            "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141",
            "description": "Handmade pasta and wood-fired pizzas.",
            "cuisine_type": "Italian",
            "location": "Whitefield, Bangalore",
            "rating": 4.3,
            "delivery_time": "30-40 min"
        },
        {
            "name": "Taco Temple", 
            "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47",
            "description": "Vibrant Mexican street tacos and quesadillas.",
            "cuisine_type": "Mexican",
            "location": "MG Road, Bangalore",
            "rating": 4.1,
            "delivery_time": "25-35 min"
        },
        {
            "name": "Morning Dew", 
            "image_url": "https://images.unsplash.com/photo-1496044534511-c03ca092ed94",
            "description": "Classic South Indian breakfast that feels like home.",
            "cuisine_type": "South Indian",
            "location": "Jayanagar, Bangalore",
            "rating": 4.6,
            "delivery_time": "15-20 min"
        },
        {
            "name": "Wok & Roll", 
            "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19",
            "description": "Fast-paced Indo-Chinese with bold flavors.",
            "cuisine_type": "Chinese",
            "location": "Electronic City, Bangalore",
            "rating": 3.9,
            "delivery_time": "20-30 min"
        },
        {
            "name": "Steak House HQ", 
            "image_url": "https://images.unsplash.com/photo-1546241072-48010ad28c2c",
            "description": "Premium cuts and grilled specialties.",
            "cuisine_type": "Steakhouse",
            "location": "Koramangala, Bangalore",
            "rating": 4.4,
            "delivery_time": "45-55 min"
        },
        {
            "name": "Sweet Obsession", 
            "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777",
            "description": "Heavenly desserts and decadent shakes.",
            "cuisine_type": "Desserts",
            "location": "Indiranagar, Bangalore",
            "rating": 4.7,
            "delivery_time": "10-15 min"
        }
    ]

    items_data = {
        "The Green Bowl": [
            {"name": "Quinoa Salad", "price": 280, "diet_tags": "Veg, Vegan", "mood_tags": "healthy", "ingredients": "Quinoa, Kale, Chickpeas, Lemon, Olive Oil"},
            {"name": "Avocado Toast", "price": 320, "diet_tags": "Veg", "mood_tags": "healthy", "ingredients": "Sourdough, Avocado, Chili Flakes, Seeds"},
            {"name": "Berry Smoothie Bowl", "price": 350, "diet_tags": "Veg, Vegan", "mood_tags": "healthy", "ingredients": "Blueberries, Bananas, Almond Milk, Granola"}
        ],
        "Spice Route": [
            {"name": "Butter Chicken", "price": 450, "diet_tags": "Non-Veg", "mood_tags": "comfort", "ingredients": "Chicken, Butter, Cream, Tomato, Spices"},
            {"name": "Paneer Tikka Masala", "price": 380, "diet_tags": "Veg", "mood_tags": "spicy", "ingredients": "Paneer, Onion, Capsicum, Yogurt, Spices"},
            {"name": "Garlic Naan", "price": 80, "diet_tags": "Veg", "mood_tags": "comfort", "ingredients": "Flour, Yeast, Garlic, Butter"}
        ],
        "Burger Haven": [
            {"name": "Classic Cheeseburger", "price": 250, "diet_tags": "Non-Veg", "mood_tags": "cheat", "ingredients": "Beef Patty, Cheese, Lettuce, Tomato, Bun"},
            {"name": "Spicy Zinger Burger", "price": 280, "diet_tags": "Non-Veg", "mood_tags": "spicy", "ingredients": "Crispy Chicken, Spicy Sauce, Lettuce, Bun"},
            {"name": "Loaded Fries", "price": 180, "diet_tags": "Veg", "mood_tags": "cheat", "ingredients": "Potato, Cheese Sauce, Jalapenos"}
        ],
        "Sushi Zen": [
            {"name": "Salmon Nigiri", "price": 550, "diet_tags": "Non-Veg", "mood_tags": "healthy", "ingredients": "Salmon, Rice, Wasabi"},
            {"name": "California Roll", "price": 480, "diet_tags": "Non-Veg", "mood_tags": "healthy", "ingredients": "Crab Stick, Avocado, Cucumber, Seaweed"},
            {"name": "Miso Soup", "price": 150, "diet_tags": "Veg", "mood_tags": "healthy", "ingredients": "Tofu, Seaweed, Green Onion, Miso Paste"}
        ],
        "Pasta Paradiso": [
            {"name": "Spaghetti Carbonara", "price": 420, "diet_tags": "Non-Veg", "mood_tags": "comfort", "ingredients": "Spaghetti, Egg, Bacon, Parmesan, Black Pepper"},
            {"name": "Lasagna Bolognese", "price": 480, "diet_tags": "Non-Veg", "mood_tags": "comfort", "ingredients": "Beef, Pasta sheets, Tomato Sauce, Bechamel, Cheese"},
            {"name": "Pesto Penne", "price": 380, "diet_tags": "Veg", "mood_tags": "healthy", "ingredients": "Penne, Basil Pesto, Parmesan, Pine Nuts"}
        ],
        "Taco Temple": [
            {"name": "Beef Tacos", "price": 320, "diet_tags": "Non-Veg", "mood_tags": "spicy", "ingredients": "Minced Beef, Corn Tortilla, Salsa, Onion, Cilantro"},
            {"name": "Chicken Quesadilla", "price": 350, "diet_tags": "Non-Veg", "mood_tags": "comfort", "ingredients": "Chicken, Flour Tortilla, Cheese, Bell Peppers"},
            {"name": "Nachos Supreme", "price": 250, "diet_tags": "Veg", "mood_tags": "cheat", "ingredients": "Corn Chips, Beans, Cheese, Sour Cream, Salsa"}
        ],
        "Morning Dew": [
            {"name": "Classic Idli", "price": 120, "diet_tags": "Veg", "mood_tags": "healthy", "ingredients": "Rice, Lentils, Sambar, Coconut Chutney"},
            {"name": "Masala Dosa", "price": 180, "diet_tags": "Veg", "mood_tags": "comfort", "ingredients": "Rice Batter, Potato Masala, Ghee, Chutney"},
            {"name": "Poha", "price": 100, "diet_tags": "Veg", "mood_tags": "healthy", "ingredients": "Flattened Rice, Onion, Peanut, Turmeric"}
        ],
        "Wok & Roll": [
            {"name": "Chicken Hakka Noodles", "price": 320, "diet_tags": "Non-Veg", "mood_tags": "comfort", "ingredients": "Noodles, Chicken strips, Cabbage, Carrot, Soy Sauce"},
            {"name": "Veg Manchurian", "price": 280, "diet_tags": "Veg", "mood_tags": "spicy", "ingredients": "Veg balls, Ginger, Garlic, Chili Sauce"},
            {"name": "Fried Rice", "price": 300, "diet_tags": "Veg", "mood_tags": "comfort", "ingredients": "Rice, Peas, Corn, Spring Onion, Egg"}
        ],
        "Steak House HQ": [
            {"name": "Ribeye Steak", "price": 1200, "diet_tags": "Non-Veg", "mood_tags": "cheat", "ingredients": "Beef Ribeye, Garlic Butter, Thyme, Rosemary"},
            {"name": "Grilled Chicken Breast", "price": 450, "diet_tags": "Non-Veg", "mood_tags": "healthy", "ingredients": "Chicken, Lemon, Asparagus, Mash"},
            {"name": "Mousaka", "price": 550, "diet_tags": "Non-Veg", "mood_tags": "comfort", "ingredients": "Eggplant, Lamb, Bechamel, Tomato"}
        ],
        "Sweet Obsession": [
            {"name": "Chocolate Lava Cake", "price": 250, "diet_tags": "Veg", "mood_tags": "cheat", "ingredients": "Chocolate, Flour, Sugar, Egg, Cocoa"},
            {"name": "Fruit Custard", "price": 180, "diet_tags": "Veg", "mood_tags": "healthy", "ingredients": "Milk, Custard Powder, Apple, Pomegranate, Grapes"},
            {"name": "New York Cheesecake", "price": 320, "diet_tags": "Veg", "mood_tags": "comfort", "ingredients": "Cream Cheese, Biscuit Base, Sugar, Berry Jam"}
        ]
    }

    comments = [
        "Absolutely delicious, will order again!",
        "The flavor profile was amazing.",
        "A bit spicy for my taste, but very fresh.",
        "Authentic taste, reminded me of home.",
        "Healthy yet filling.",
        "Perfect comfort food for a rainy day.",
        "Best dessert I have had in a long time!"
    ]

    for rest_info in restaurants_data:
        rest = Restaurant.objects.create(**rest_info)
        items = items_data.get(rest.name, [])
        for item_info in items:
            mi = MenuItem.objects.create(restaurant=rest, **item_info)
            # Seed ingredient options from the comma-separated `ingredients` text
            raw = (item_info.get('ingredients') or '').split(',')
            for idx, name in enumerate([n.strip() for n in raw if n.strip()][:6]):
                MenuItemIngredientOption.objects.get_or_create(
                    menu_item=mi, name=name.title(),
                    defaults={'is_default': True, 'extra_price': 0, 'is_active': True},
                )
            # Add some reviews
            Review.objects.create(
                user=user,
                restaurant=rest,
                menu_item=mi,
                rating=random.randint(4, 5),
                comment=random.choice(comments)
            )
            
    print(f"Successfully seeded {Restaurant.objects.count()} restaurants and {MenuItem.objects.count()} menu items.")

if __name__ == "__main__":
    seed_data()
