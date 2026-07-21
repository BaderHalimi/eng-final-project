
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/', views.add_to_cart, name='add'),
    path('update/', views.update_cart_item, name='update'),
    path('remove/', views.remove_from_cart, name='remove'),
    path('clear/', views.clear_cart, name='clear'),
    
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='wishlist_add'),
    path('wishlist/remove/', views.remove_from_wishlist, name='wishlist_remove'),
]

