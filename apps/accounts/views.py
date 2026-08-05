from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .models import User
from .forms import LoginForm, UserCreateForm, UserUpdateForm, ProfileForm
from .decorators import admin_required, tenant_required


@login_required
@admin_required
def user_list(request):
    """List all users for the current tenant."""
    users = User.objects.filter(tenant=request.tenant).order_by('first_name')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
@admin_required
def user_create(request):
    """Create a new user for the current tenant."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tenant = request.tenant
            user.save()
            messages.success(request, f'Usuário "{user.username}" criado com sucesso.')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Novo Usuário'})


@login_required
@admin_required
def user_update(request, pk):
    """Update an existing user."""
    user = get_object_or_404(User, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário "{user.username}" atualizado.')
            return redirect('accounts:user_list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'Editar: {user.username}'})


@login_required
@admin_required
def user_delete(request, pk):
    """Delete a user."""
    user = get_object_or_404(User, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário "{username}" removido.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'object': user})


@login_required
def profile(request):
    """User profile view and edit."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password(request):
    """Change password view."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    for field in form.fields.values():
        field.widget.attrs['class'] = (
            'w-full px-4 py-2 border border-gray-300 rounded-lg '
            'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        )
    return render(request, 'accounts/change_password.html', {'form': form})
