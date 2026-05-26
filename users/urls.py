from django.urls import path
from .views import (
    AddressDetailView,
    AddressListCreateView,
    CreateUserProfileView,
    ProfileMeView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    path('profile/',             CreateUserProfileView.as_view(), name='create-user-profile'),
    path('profile/me/',          ProfileMeView.as_view(),         name='profile-me'),
    path('addresses/',           AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/',  AddressDetailView.as_view(),     name='address-detail'),
    path('',                     UserListCreateView.as_view(),    name='user-list-create'),
    path('<int:pk>/',            UserDetailView.as_view(),        name='user-detail'),
]
