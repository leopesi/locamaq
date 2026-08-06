from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path
from . import views


def logout_view(request):
    """Logout that accepts both GET and POST. Redirects to tenant landing if available."""
    tenant = getattr(request, 'tenant', None) or (request.user.tenant if request.user.is_authenticated and hasattr(request.user, 'tenant') else None)
    slug = tenant.slug if tenant and tenant.slug else None
    logout(request)
    if slug:
        return redirect('tenants:tenant_landing', slug=slug)
    return redirect('/')


app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
]
