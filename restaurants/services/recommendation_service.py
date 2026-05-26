from decimal import Decimal

from django.db.models import Avg

from restaurants.models import MenuItem
from restaurants.nlp_service import detect_allergy_risk


MOOD_ALIASES = {
    'cheat_meal': 'cheat',
    'cheat-meal': 'cheat',
    'late_night': 'late-night',
}

# Time-of-day keyword profiles. Items whose text matches these get a boost.
TIME_KEYWORDS = {
    'morning': {
        'breakfast', 'idli', 'dosa', 'poha', 'upma', 'paratha', 'omelette',
        'omelet', 'eggs', 'pancake', 'pancakes', 'waffle', 'waffles',
        'oats', 'porridge', 'muesli', 'granola', 'smoothie', 'juice',
        'coffee', 'tea', 'toast', 'sandwich', 'bagel', 'cereal',
        'yogurt', 'yoghurt', 'fruit',
    },
    'afternoon': {
        'lunch', 'rice', 'thali', 'biryani', 'curry', 'dal', 'roti',
        'naan', 'bowl', 'salad', 'wrap', 'sandwich', 'pasta', 'noodles',
        'burger', 'pizza', 'meals',
    },
    'evening': {
        'snack', 'snacks', 'samosa', 'pakora', 'pakoda', 'chaat',
        'vada', 'momos', 'momo', 'sandwich', 'wrap', 'burger', 'fries',
        'tea', 'coffee', 'pastry', 'cake', 'cookie', 'cookies',
        'milkshake', 'shake', 'mocktail',
    },
    'night': {
        'dinner', 'curry', 'biryani', 'pasta', 'pizza', 'rice',
        'roti', 'naan', 'soup', 'noodles', 'tikka', 'kebab',
        'steak', 'grill', 'bowl',
    },
    'late-night': {
        'light', 'soup', 'sandwich', 'snack', 'toast', 'poha', 'idli',
        'smoothie', 'noodle', 'noodles', 'wrap', 'maggi',
    },
}


def _parse_allergies(raw_allergies):
    if raw_allergies is None:
        return []
    if isinstance(raw_allergies, str):
        raw_allergies = raw_allergies.split(',')
    allergies = []
    for allergy in raw_allergies:
        allergies.extend(
            part.strip()
            for part in str(allergy).split(',')
            if part.strip()
        )
    return allergies


def _normalize_tag(value):
    normalized = str(value or '').strip().lower().replace('_', '-').replace(' ', '-')
    return MOOD_ALIASES.get(normalized, normalized)


def _item_text(item):
    return ' '.join(
        str(value)
        for value in [
            getattr(item, 'name', ''),
            getattr(item, 'description', ''),
            getattr(item, 'diet_tags', ''),
            getattr(item, 'mood_tags', ''),
            getattr(item, 'ingredients', ''),
        ]
        if value
    )


def _item_tokens(item):
    return {
        token.strip().lower()
        for token in _item_text(item).replace(',', ' ').replace('-', ' ').split()
        if token.strip()
    }


def _matches_mood(item, mood):
    if not mood:
        return False
    expected = _normalize_tag(mood)
    item_mood = _normalize_tag(getattr(item, 'mood_tags', ''))
    return expected == item_mood or expected in _item_tokens(item)


def _diet_tokens(value):
    text = str(value or '').lower().replace('-', ' ').replace('_', ' ')
    tokens = set(text.replace(',', ' ').split())
    if 'non' in tokens or 'nonveg' in tokens or 'nonvegetarian' in tokens:
        return {'non_vegetarian'}
    if 'vegan' in tokens:
        return {'vegan', 'vegetarian'}
    if 'veg' in tokens or 'vegetarian' in tokens:
        return {'vegetarian'}
    return tokens


def _matches_diet(item, diet):
    user_tokens = _diet_tokens(diet)
    if not user_tokens or 'no' in user_tokens or 'preference' in user_tokens:
        return False
    item_tokens = _diet_tokens(getattr(item, 'diet_tags', ''))
    if 'vegan' in user_tokens:
        return 'vegan' in item_tokens
    if 'vegetarian' in user_tokens:
        return 'vegetarian' in item_tokens or 'vegan' in item_tokens
    if 'non_vegetarian' in user_tokens:
        return 'non_vegetarian' in item_tokens
    return False


def _item_rating(item, restaurant):
    rating = getattr(item, 'avg_rating', None)
    if rating is None:
        rating = getattr(restaurant, 'rating', None)
    if rating is None:
        return 0.0
    if isinstance(rating, Decimal):
        return float(rating)
    return float(rating)


def _matches_time(item, time_key):
    keywords = TIME_KEYWORDS.get(time_key)
    if not keywords:
        return False
    return bool(_item_tokens(item).intersection(keywords))


TIME_LABELS = {
    'morning':    'great for morning',
    'afternoon':  'great for lunch',
    'evening':    'great evening snack',
    'night':      'great for dinner',
    'late-night': 'good late-night option',
}


def get_recommendations(user, restaurant, mood=None, time=None):
    allergies = _parse_allergies(getattr(user, 'allergies', ''))
    diet = getattr(user, 'diet_preferences', '')
    time_key = _normalize_tag(time)

    items = (
        MenuItem.objects
        .filter(restaurant=restaurant)
        .annotate(avg_rating=Avg('review__rating'))
    )

    recommendations = []

    for item in items:
        allergy_result = detect_allergy_risk(allergies, _item_text(item))
        if not allergy_result['safe']:
            continue

        score = 0.0
        reasons = []

        if _matches_mood(item, mood):
            score += 3
            reasons.append('matches your mood')

        if _matches_diet(item, diet):
            score += 2
            reasons.append('fits your diet')

        rating = _item_rating(item, restaurant)
        if rating > 0:
            score += rating / 2
            reasons.append('popular choice')

        if time_key in TIME_KEYWORDS and _matches_time(item, time_key):
            score += 1.5
            reasons.append(TIME_LABELS[time_key])

        recommendations.append({
            'item': item,
            'score': round(score, 2),
            'reasons': reasons,
        })

    recommendations.sort(key=lambda result: result['score'], reverse=True)
    return recommendations[:5]
