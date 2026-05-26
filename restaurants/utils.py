from .nlp_service import detect_allergy_risk


def check_allergy_risk(user_allergies, ingredients):
    if isinstance(ingredients, (list, tuple, set)):
        text = ' '.join(str(ingredient) for ingredient in ingredients)
    else:
        text = str(ingredients or '')
    return not detect_allergy_risk(user_allergies, text)['safe']
