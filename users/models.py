from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user             = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    name             = models.CharField(max_length=100)
    email            = models.EmailField(unique=True)
    phone            = models.CharField(max_length=20, blank=True, default='')
    allergies        = models.TextField(blank=True)
    diet_preferences = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class UserAddress(models.Model):
    user         = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')
    # Legacy compact field kept for back-compat; recomputed on save.
    address_line = models.CharField(max_length=255, blank=True, default='')
    # New structured fields (Task: complete address workflow)
    full_name    = models.CharField(max_length=120, blank=True, default='')
    phone        = models.CharField(max_length=20,  blank=True, default='')
    house        = models.CharField(max_length=120, blank=True, default='')
    street       = models.CharField(max_length=200, blank=True, default='')
    city         = models.CharField(max_length=100, blank=True, default='Bangalore')
    state        = models.CharField(max_length=100, blank=True, default='')
    pincode      = models.CharField(max_length=10,  blank=True, default='')
    is_default   = models.BooleanField(default=False)
    address_type = models.CharField(max_length=20,  default='Home')  # Home | Office | Other

    def save(self, *args, **kwargs):
        # Keep legacy address_line in sync with structured fields so old
        # serializers / pages keep rendering even when only structured data is set.
        parts = [p for p in [self.house, self.street, self.city, self.state, self.pincode] if p]
        composed = ', '.join(parts)
        if composed:
            self.address_line = composed[:255]
        elif not self.address_line:
            self.address_line = '—'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.address_line} ({self.address_type})'
