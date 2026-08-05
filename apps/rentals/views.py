from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Rental, RentalItem
from .forms import RentalForm, RentalItemForm, RentalReturnForm, RentalEditForm
from .services.geocoding import geocode_address
from .services.routing import estimate_delivery_time
from apps.inventory.models import Equipment, EquipmentHistory
from apps.finance.models import Transaction
from apps.core.cache import invalidate_on_write


@login_required
def rental_list(request):
    """List rentals with filters."""
    queryset = Rental.objects.filter(tenant=request.tenant)

    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '').strip()

    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if search:
        queryset = queryset.filter(customer__name__icontains=search)

    rentals = queryset.select_related('customer').order_by('-created_at')

    return render(request, 'rentals/rental_list.html', {
        'rentals': rentals,
        'status_filter': status_filter,
        'search': search,
        'statuses': Rental.Status.choices,
    })


@login_required
@invalidate_on_write
def rental_create(request):
    """Create a new rental with equipment in a single form."""
    if request.method == 'POST':
        form = RentalForm(request.tenant, request.POST)
        if form.is_valid():
            # Create rental
            rental = form.save(commit=False)
            rental.tenant = request.tenant
            rental.created_by = request.user

            # Montar endereço completo a partir dos campos estruturados
            street = form.cleaned_data.get('delivery_street', '')
            number = form.cleaned_data.get('delivery_number', '')
            complement = form.cleaned_data.get('delivery_complement', '')
            neighborhood = form.cleaned_data.get('delivery_neighborhood', '')
            city = form.cleaned_data.get('delivery_city', 'Araguari')
            state = form.cleaned_data.get('delivery_state', 'MG')

            parts = [f'{street}, {number}']
            if complement:
                parts.append(complement)
            parts.append(f'{neighborhood} - {city}/{state}')
            rental.delivery_address = ', '.join(parts)

            rental.delivery_reference = form.cleaned_data.get('delivery_reference', '')
            rental.delivery_contact = form.cleaned_data.get('delivery_contact', '')
            rental.delivery_phone = form.cleaned_data.get('delivery_phone', '')

            # Geocode delivery address
            if rental.delivery_address:
                lat, lng = geocode_address(rental.delivery_address)
                rental.delivery_lat = lat
                rental.delivery_lng = lng

                # Calcular tempo de entrega
                if lat and lng:
                    estimate = estimate_delivery_time(lat, lng)
                    if estimate:
                        rental.delivery_distance_km = estimate['distance_km']
                        rental.delivery_time_min = estimate['duration_min']

            rental.save()

            # Add equipment items
            for equipment, qty, value in form.get_items():
                # Determine unit value
                if not value:
                    if rental.period_type == 'daily':
                        value = equipment.daily_rate
                    elif rental.period_type == 'weekly':
                        value = equipment.weekly_rate
                    else:
                        value = equipment.monthly_rate

                RentalItem.objects.create(
                    rental=rental,
                    equipment=equipment,
                    quantity=qty,
                    unit_value=value,
                )

                # Update equipment state
                old_state = equipment.state
                equipment.state = Equipment.State.RENTED
                equipment.save()

                EquipmentHistory.objects.create(
                    equipment=equipment,
                    previous_state=old_state,
                    new_state=Equipment.State.RENTED,
                    changed_by=request.user,
                    notes=f'Locado na Locação #{rental.pk}',
                )

            # Calculate total
            rental.calculate_total()
            rental.save()

            messages.success(request, f'Locação #{rental.pk} criada com sucesso! Valor: R$ {rental.total_value}')
            return redirect('rentals:rental_detail', pk=rental.pk)
    else:
        form = RentalForm(request.tenant)

    return render(request, 'rentals/rental_form.html', {'form': form, 'title': 'Nova Locação'})


@login_required
def rental_add_item(request, pk):
    """Add more equipment items to an existing rental."""
    rental = get_object_or_404(Rental, pk=pk, tenant=request.tenant, status='active')

    if request.method == 'POST':
        form = RentalItemForm(request.tenant, request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.rental = rental
            equipment = item.equipment

            # Set unit value based on period type
            if not item.unit_value:
                if rental.period_type == 'daily':
                    item.unit_value = equipment.daily_rate
                elif rental.period_type == 'weekly':
                    item.unit_value = equipment.weekly_rate
                else:
                    item.unit_value = equipment.monthly_rate

            item.save()

            # Update equipment state
            old_state = equipment.state
            equipment.state = Equipment.State.RENTED
            equipment.save()

            EquipmentHistory.objects.create(
                equipment=equipment,
                previous_state=old_state,
                new_state=Equipment.State.RENTED,
                changed_by=request.user,
                notes=f'Locado na Locação #{rental.pk}',
            )

            # Recalculate total
            rental.calculate_total()
            rental.save()

            messages.success(request, f'Equipamento "{equipment}" adicionado.')
            return redirect('rentals:rental_add_item', pk=rental.pk)
    else:
        form = RentalItemForm(request.tenant)

    items = rental.items.select_related('equipment').all()
    return render(request, 'rentals/rental_add_item.html', {
        'rental': rental,
        'form': form,
        'items': items,
    })


@login_required
def rental_detail(request, pk):
    """Rental detail view."""
    rental = get_object_or_404(Rental, pk=pk, tenant=request.tenant)
    items = rental.items.select_related('equipment').all()
    return render(request, 'rentals/rental_detail.html', {'rental': rental, 'items': items})


@login_required
def rental_edit(request, pk):
    """Edit an existing rental."""
    rental = get_object_or_404(Rental, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        old_address = rental.delivery_address
        form = RentalEditForm(request.tenant, request.POST, instance=rental)
        if form.is_valid():
            rental = form.save(commit=False)
            # Re-geocode if address changed
            if rental.delivery_address and rental.delivery_address != old_address:
                lat, lng = geocode_address(rental.delivery_address)
                rental.delivery_lat = lat
                rental.delivery_lng = lng
            rental.save()
            messages.success(request, f'Locação #{rental.pk} atualizada.')
            return redirect('rentals:rental_detail', pk=rental.pk)
    else:
        form = RentalEditForm(request.tenant, instance=rental)
    return render(request, 'rentals/rental_edit.html', {'form': form, 'rental': rental})


@login_required
@invalidate_on_write
def rental_return(request, pk):
    """Process rental return."""
    rental = get_object_or_404(Rental, pk=pk, tenant=request.tenant, status='active')

    if request.method == 'POST':
        form = RentalReturnForm(request.POST)
        if form.is_valid():
            rental.actual_return = form.cleaned_data['actual_return']
            rental.status = Rental.Status.RETURNED
            if form.cleaned_data['notes']:
                rental.notes += f'\nDevolução: {form.cleaned_data["notes"]}'
            rental.save()

            # Return all equipment to available
            for item in rental.items.select_related('equipment').all():
                eq = item.equipment
                old_state = eq.state
                eq.state = Equipment.State.AVAILABLE
                eq.save()
                EquipmentHistory.objects.create(
                    equipment=eq,
                    previous_state=old_state,
                    new_state=Equipment.State.AVAILABLE,
                    changed_by=request.user,
                    notes=f'Devolvido da Locação #{rental.pk}',
                )

            # Create financial transaction
            Transaction.objects.create(
                tenant=request.tenant,
                type=Transaction.Type.INCOME,
                value=rental.total_value,
                description=f'Recebimento Locação #{rental.pk} - {rental.customer.name}',
                date=form.cleaned_data['actual_return'],
                rental=rental,
                created_by=request.user,
            )

            messages.success(request, f'Locação #{rental.pk} devolvida. Entrada de R$ {rental.total_value} registrada.')
            return redirect('rentals:rental_detail', pk=rental.pk)
    else:
        form = RentalReturnForm(initial={'actual_return': timezone.now().date()})

    return render(request, 'rentals/rental_return.html', {'rental': rental, 'form': form})


@login_required
@invalidate_on_write
def rental_cancel(request, pk):
    """Cancel a rental."""
    rental = get_object_or_404(Rental, pk=pk, tenant=request.tenant, status='active')

    if request.method == 'POST':
        rental.status = Rental.Status.CANCELLED
        rental.save()

        # Return all equipment to available
        for item in rental.items.select_related('equipment').all():
            eq = item.equipment
            old_state = eq.state
            eq.state = Equipment.State.AVAILABLE
            eq.save()
            EquipmentHistory.objects.create(
                equipment=eq,
                previous_state=old_state,
                new_state=Equipment.State.AVAILABLE,
                changed_by=request.user,
                notes=f'Cancelamento da Locação #{rental.pk}',
            )

        messages.success(request, f'Locação #{rental.pk} cancelada.')
        return redirect('rentals:rental_list')

    return render(request, 'rentals/rental_cancel.html', {'rental': rental})
