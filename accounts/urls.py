"""
Accounts URLs - SECURE VERSION
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('addresses/', views.addresses_view, name='addresses'),
    path('address/add/', views.add_address_view, name='add_address'),
    path('address/<uuid:address_id>/delete/', views.delete_address_view, name='delete_address'),
    path('address/<uuid:address_id>/set-default/', views.set_default_address_view, name='set_default_address'),
    

    path('password-reset/', views.SecurePasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.SecurePasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    

    path('api/users/search/', views.user_search, name='api_user_search'),
    path('api/users/export/', views.export_user_data, name='api_export_user_data'),
    path('api/users/debug/', views.debug_user_info, name='api_debug_user_info'),
    path('api/users/update-email/', views.update_email, name='api_update_email'),
    path('api/password/weak-reset/', views.weak_password_reset, name='api_weak_password_reset'),
    path('api/admin/action/', views.admin_action, name='api_admin_action'),
]
