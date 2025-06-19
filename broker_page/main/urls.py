from django.urls import path
from . import views
from broker_page.admin_views import get_colony_suggestions

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('agent-registration/', views.agent_registration, name='agent_registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('payment-handler/', views.payment_handler, name='payment_handler'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('search/', views.search_brokers, name='search_brokers'),
    # Dashboard and profile pages using new slug format (full-name-contact-number)
    path('<str:slug>/dashboard/', views.dashboard, name='dashboard'),
    path('<str:slug>/', views.broker_profile, name='broker_profile'),
    
    # API endpoints
    path('api/colony-suggestions/', get_colony_suggestions, name='colony_suggestions'),
]