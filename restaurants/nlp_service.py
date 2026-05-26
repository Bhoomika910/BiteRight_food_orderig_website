import re


ALLERGY_MAP = {
    'nuts': [
        'peanut',
        'peanuts',
        'almond',
        'almonds',
        'cashew',
        'cashews',
        'walnut',
        'walnuts',
        'pistachio',
        'pistachios',
        'hazelnut',
        'hazelnuts',
        'pecan',
        'pecans',
    ],
    'dairy': [
        'milk',
        'cheese',
        'butter',
        'cream',
        'curd',
        'paneer',
        'yogurt',
        'yoghurt',
        'ghee',
        'whey',
        'casein',
    ],
    'shellfish': [
        'shrimp',
        'prawn',
        'prawns',
        'crab',
        'crabs',
        'lobster',
        'lobsters',
        'clam',
        'clams',
        'oyster',
        'oysters',
        'mussel',
        'mussels',
    ],
    'gluten': [
        'wheat',
        'flour',
        'maida',
        'barley',
        'rye',
        'semolina',
        'sooji',
        'bread',
        'pasta',
        'noodles',
    ],
    'soy': [
        'soy',
        'soya',
        'tofu',
        'edamame',
        'tempeh',
    ],
    'egg': [
        'egg',
        'eggs',
        'mayonnaise',
        'mayo',
    ],
    'fish': [
        'fish',
        'salmon',
        'tuna',
        'cod',
        'anchovy',
        'anchovies',
        'sardine',
        'sardines',
    ],
    'sesame': [
        'sesame',
        'tahini',
    ],
}


def _tokenize(text):
    return re.findall(r'[a-z0-9]+', str(text).lower())


def _singularize(token):
    return token[:-1] if len(token) > 3 and token.endswith('s') else token


def _expand_allergy_keywords(user_allergies):
    keywords = set()

    for allergy in user_allergies or []:
        for token in _tokenize(allergy):
            normalized = _singularize(token)
            keywords.add(token)
            keywords.add(normalized)

            if normalized == 'nut':
                for alias in ALLERGY_MAP['nuts']:
                    keywords.update(_tokenize(alias))

            for alias in ALLERGY_MAP.get(token, []):
                keywords.update(_tokenize(alias))

            for alias in ALLERGY_MAP.get(normalized, []):
                keywords.update(_tokenize(alias))

            for category, aliases in ALLERGY_MAP.items():
                alias_tokens = {_singularize(alias_token) for alias in aliases for alias_token in _tokenize(alias)}
                if normalized in alias_tokens:
                    keywords.add(category)
                    for alias in aliases:
                        keywords.update(_tokenize(alias))

    return {keyword for keyword in keywords if keyword}


def detect_allergy_risk(user_allergies: list[str], text: str) -> dict:
    text_tokens = set(_tokenize(text))
    allergy_keywords = _expand_allergy_keywords(user_allergies)
    matched_allergens = sorted(text_tokens.intersection(allergy_keywords))

    return {
        'safe': not matched_allergens,
        'matched_allergens': matched_allergens,
    }
