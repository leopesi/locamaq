from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('', views.promotion_list, name='promotion_list'),
    path('create/', views.promotion_create, name='promotion_create'),
    path('<int:pk>/edit/', views.promotion_edit, name='promotion_edit'),
    path('<int:pk>/send/', views.promotion_send, name='promotion_send'),
]
