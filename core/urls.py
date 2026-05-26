from django.contrib import admin
from django.urls    import include, path, re_path
from .views         import frontend_root, frontend_page, health_check

urlpatterns = [
    path('',        frontend_root),
    path('admin/',  admin.site.urls),
    path('health/', health_check),

    path('api/users/',   include('users.urls')),
    path('api/',         include('restaurants.urls')),
    path('api/',         include('orders.urls')),

    re_path(
        r'^(?P<page>(index|login|restaurants|menu|item|cart|orders|recommendations|payment|payment-success|addresses)\.html)$',
        frontend_page,
    ),
]
