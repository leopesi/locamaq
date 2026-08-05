from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.rental_list, name='rental_list'),
    path('create/', views.rental_create, name='rental_create'),
    path('<int:pk>/', views.rental_detail, name='rental_detail'),
    path('<int:pk>/edit/', views.rental_edit, name='rental_edit'),
    path('<int:pk>/add-item/', views.rental_add_item, name='rental_add_item'),
    path('<int:pk>/return/', views.rental_return, name='rental_return'),
    path('<int:pk>/cancel/', views.rental_cancel, name='rental_cancel'),
]
