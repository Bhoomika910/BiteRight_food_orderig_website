"""Helpers for the one-to-one link between Django User and UserProfile."""

from django.contrib.auth import get_user_model


def get_or_create_profile(user):
    """
    Return request.user.profile, creating a minimal UserProfile if missing.
    Keeps profile.email aligned with user.email when possible.
    """
    if getattr(user, 'is_anonymous', True):
        raise ValueError('Cannot create profile for anonymous user')

    profile = getattr(user, 'profile', None)
    if profile is not None:
        return profile

    from users.models import UserProfile

    email = (getattr(user, 'email', '') or '').strip().lower()
    if not email:
        email = f'user-{user.pk}@biteright.local'

    base = email.rsplit('@', 1)[0] if '@' in email else email
    candidate = email
    suffix = 0
    while UserProfile.objects.filter(email=candidate).exclude(user=user).exists():
        suffix += 1
        candidate = f'{base}+{suffix}@biteright.local' if '@' in email else f'{email}+{suffix}'

    name = user.get_full_name() or user.get_username() or candidate.split('@')[0]
    return UserProfile.objects.create(
        user=user,
        name=name[:100],
        email=candidate,
        allergies='',
        diet_preferences='',
    )


def unique_username_for_email(email: str) -> str:
    """Reserve a unique auth User.username derived from email (max 150 chars)."""
    User = get_user_model()
    base = (email or '').strip().lower()[:150]
    if not base:
        base = 'user'
    candidate = base
    n = 0
    while User.objects.filter(username=candidate).exists():
        n += 1
        suffix = f'_{n}'
        candidate = (base[: 150 - len(suffix)] + suffix)
    return candidate
