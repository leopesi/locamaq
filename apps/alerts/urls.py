from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Notifications
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/read/', views.notification_mark_read, name='mark_read'),
    path('<int:pk>/dismiss/', views.notification_dismiss, name='dismiss'),
    path('mark-all-read/', views.notification_mark_all_read, name='mark_all_read'),
    path('run-checks/', views.alert_run_checks, name='run_checks'),

    # Setup
    path('setup/', views.alert_setup, name='setup'),
    path('setup/create/', views.alert_rule_create, name='rule_create'),
    path('setup/<int:pk>/edit/', views.alert_rule_edit, name='rule_edit'),
    path('setup/<int:pk>/delete/', views.alert_rule_delete, name='rule_delete'),
]
