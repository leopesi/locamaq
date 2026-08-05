from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('rental/<int:rental_id>/pdf/', views.generate_pdf, name='generate_pdf'),
]
