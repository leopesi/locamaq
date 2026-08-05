from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('rental/<int:rental_id>/send-receipt/', views.send_receipt_whatsapp, name='send_receipt'),
    path('rental/<int:rental_id>/notify/', views.send_notification, name='send_notification'),
]
