from django.urls import path
from . import admin_views

app_name = 'custom_admin'

urlpatterns = [
    path('login/', admin_views.admin_login, name='admin_login'),
    path('logout/', admin_views.admin_logout, name='admin_logout'),
    path('', admin_views.admin_login, name='admin_root'),  # redirect /admin/ to login
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('users/', admin_views.admin_users, name='admin_users'),
    path('user/<int:broker_id>/', admin_views.admin_view_details, name='admin_view_details'),
    path('user/<int:broker_id>/toggle_verification/', admin_views.admin_toggle_verification, name='admin_toggle_verification'),
    
    # Colony management URLs
    path('colonies/', admin_views.admin_colonies, name='admin_colonies'),
    path('colonies/add/', admin_views.admin_add_colony, name='add_colony'),
    path('colonies/<int:colony_id>/edit/', admin_views.admin_edit_colony, name='edit_colony'),
    path('colonies/delete/', admin_views.admin_delete_colony, name='delete_colony'),
    path('colonies/export/', admin_views.admin_export_colonies, name='export_colonies'),
    path('colonies/import/', admin_views.admin_import_colonies, name='import_colonies'),
    path('colonies/download-template/', admin_views.admin_download_colonies_template, name='download_colonies_template'),
    
    # API endpoints
    path('api/colony-suggestions/', admin_views.get_colony_suggestions, name='colony_suggestions'),
] 