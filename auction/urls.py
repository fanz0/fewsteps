from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('home_page', views.home_page, name='home_page'),
    path('auctions', views.auctions, name='auctions'),
    path('update_bid/<pk>', views.update_bid, name='update_bid'),
] 