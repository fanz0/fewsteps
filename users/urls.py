from django.urls import path
from . import views

urlpatterns = [
    path('register_user', views.register_user, name='register_user'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('profile_user', views.profile, name='profile_user'),
    path('bio_edit', views.bio_edit, name='bio_edit'),
]