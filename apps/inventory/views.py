from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Equipment, EquipmentHistory
from .forms import EquipmentForm


@login_required
def equipment_list(request):
    """List equipment with filters."""
    queryset = Equipment.objects.filter(tenant=request.tenant)

    search = request.GET.get('q', '').strip()
    state_filter = request.GET.get('state', '')
    category_filter = request.GET.get('category', '')

    if search:
        queryset = queryset.filter(
            Q(code__icontains=search) | Q(name__icontains=search)
        )
    if state_filter:
        queryset = queryset.filter(state=state_filter)
    if category_filter:
        queryset = queryset.filter(category=category_filter)

    equipments = queryset.order_by('code')

    # Stats
    total = Equipment.objects.filter(tenant=request.tenant).count()
    available = Equipment.objects.filter(tenant=request.tenant, state='available').count()
    rented = Equipment.objects.filter(tenant=request.tenant, state='rented').count()
    maintenance = Equipment.objects.filter(tenant=request.tenant, state='maintenance').count()

    return render(request, 'inventory/equipment_list.html', {
        'equipments': equipments,
        'search': search,
        'state_filter': state_filter,
        'category_filter': category_filter,
        'states': Equipment.State.choices,
        'categories': Equipment.Category.choices,
        'stats': {'total': total, 'available': available, 'rented': rented, 'maintenance': maintenance},
    })


@login_required
def equipment_create(request):
    """Create a new equipment."""
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.tenant = request.tenant
            equipment.save()
            messages.success(request, f'Equipamento "{equipment}" cadastrado.')
            return redirect('inventory:equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'inventory/equipment_form.html', {'form': form, 'title': 'Novo Equipamento'})


@login_required
def equipment_update(request, pk):
    """Update an existing equipment."""
    equipment = get_object_or_404(Equipment, pk=pk, tenant=request.tenant)
    old_state = equipment.state

    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            equipment = form.save()
            # Log state change
            if old_state != equipment.state:
                EquipmentHistory.objects.create(
                    equipment=equipment,
                    previous_state=old_state,
                    new_state=equipment.state,
                    changed_by=request.user,
                    notes=f'Alterado manualmente via edição.',
                )
            messages.success(request, f'Equipamento "{equipment}" atualizado.')
            return redirect('inventory:equipment_list')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'inventory/equipment_form.html', {'form': form, 'title': f'Editar: {equipment}'})


@login_required
def equipment_delete(request, pk):
    """Delete an equipment."""
    equipment = get_object_or_404(Equipment, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = str(equipment)
        equipment.delete()
        messages.success(request, f'Equipamento "{name}" removido.')
        return redirect('inventory:equipment_list')
    return render(request, 'inventory/equipment_confirm_delete.html', {'object': equipment})


@login_required
def equipment_detail(request, pk):
    """Equipment detail with history."""
    equipment = get_object_or_404(Equipment, pk=pk, tenant=request.tenant)
    history = equipment.history.all()[:20]
    return render(request, 'inventory/equipment_detail.html', {
        'equipment': equipment,
        'history': history,
    })
