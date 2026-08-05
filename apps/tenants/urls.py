from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('guia/', views.guide, name='guide'),
    path('settings/', views.settings_general, name='settings_general'),
    path('settings/whatsapp/', views.settings_whatsapp, name='settings_whatsapp'),
]
