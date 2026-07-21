
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('place/', views.place_order, name='place'),
    path('', views.order_list, name='list'),
    path('<uuid:order_id>/', views.order_detail, name='detail'),
    path('<uuid:order_id>/cancel/', views.cancel_order, name='cancel'),
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
]

