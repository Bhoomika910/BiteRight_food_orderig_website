# Generated manually: link UserProfile to Django User and backfill rows.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def link_profiles_to_users(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    UserProfile = apps.get_model('users', 'UserProfile')

    for profile in UserProfile.objects.filter(user__isnull=True):
        email = (profile.email or '').strip().lower() or f'orphan-profile-{profile.pk}@biteright.local'
        username = email[:150]
        n = 0
        while User.objects.filter(username=username).exists():
            n += 1
            suffix = f'_{n}'
            username = (email[: 150 - len(suffix)] + suffix)

        # Historical migration User model has no helper methods; use unusable password marker.
        user = User.objects.create(username=username, email=email, password='!')
        profile.user = user
        profile.save(update_fields=['user'])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_useraddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='profile',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(link_profiles_to_users, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='profile',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
