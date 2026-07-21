"""
Products URLs - SECURE VERSION
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    

    path('api/search/', views.product_search_raw, name='api_product_search'),
    path('api/preview/', views.product_preview, name='api_product_preview'),
    path('api/image/', views.product_image_path, name='api_product_image'),
    path('api/report/', views.execute_report, name='api_execute_report'),
    path('api/comment/', views.product_comment, name='api_product_comment'),
    path('api/render/', views.render_template, name='api_render_template'),
]
