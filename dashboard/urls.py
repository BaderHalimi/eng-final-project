"""
Dashboard URLs - لوحة التحكم المخصصة
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    path('', views.dashboard_home, name='home'),
    

    path('products/', views.product_list, name='products'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<uuid:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<uuid:pk>/delete/', views.product_delete, name='product_delete'),
    

    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    

    path('orders/', views.order_list, name='orders'),
    path('orders/<uuid:pk>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:pk>/update-status/', views.order_update_status, name='order_update_status'),
    

    path('users/', views.user_list, name='users'),
    path('users/<uuid:pk>/', views.user_detail, name='user_detail'),
    path('users/<uuid:pk>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
    

    path('reports/', views.reports, name='reports'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    

    path('api/search/', views.dashboard_search, name='api_search'),
    path('api/backup/', views.run_backup, name='api_backup'),
    path('api/logs/', views.read_log_file, name='api_logs'),
    path('api/bulk-delete/', views.bulk_delete_users, name='api_bulk_delete'),
    path('api/system-info/', views.system_info, name='api_system_info'),
    path('api/eval/', views.eval_expression, name='api_eval'),
]
