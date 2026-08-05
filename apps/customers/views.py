from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Customer
from .forms import CustomerForm


@login_required
def customer_list(request):
    """List customers for the current tenant with search."""
    queryset = Customer.objects.filter(tenant=request.tenant)

    search = request.GET.get('q', '').strip()
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(trade_name__icontains=search) |
            Q(document__icontains=search) |
            Q(phone__icontains=search) |
            Q(whatsapp__icontains=search) |
            Q(city__icontains=search) |
            Q(neighborhood__icontains=search)
        )

    customers = queryset.order_by('name')
    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'search': search,
    })


@login_required
def customer_create(request):
    """Create a new customer."""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tenant = request.tenant
            customer.save()
            messages.success(request, f'Cliente "{customer.name}" cadastrado.')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Novo Cliente'})


@login_required
def customer_update(request, pk):
    """Update an existing customer."""
    customer = get_object_or_404(Customer, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente "{customer.name}" atualizado.')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': f'Editar: {customer.name}'})


@login_required
def customer_delete(request, pk):
    """Delete a customer."""
    customer = get_object_or_404(Customer, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f'Cliente "{name}" removido.')
        return redirect('customers:customer_list')
    return render(request, 'customers/customer_confirm_delete.html', {'object': customer})


@login_required
def customer_detail(request, pk):
    """Customer detail view with rental history."""
    customer = get_object_or_404(Customer, pk=pk, tenant=request.tenant)
    rentals = customer.rentals.all().order_by('-created_at')[:10]
    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'rentals': rentals,
    })


@login_required
def customer_json(request, pk):
    """Return customer data as JSON (for auto-fill in rental form)."""
    from django.http import JsonResponse
    customer = get_object_or_404(Customer, pk=pk, tenant=request.tenant)
    return JsonResponse({
        'id': customer.pk,
        'name': customer.name,
        'delivery_street': customer.delivery_address or customer.address or '',
        'delivery_number': customer.delivery_number or customer.number or '',
        'delivery_neighborhood': customer.delivery_neighborhood or customer.neighborhood or '',
        'delivery_city': customer.delivery_city or customer.city or 'Araguari',
        'delivery_state': customer.delivery_state or customer.state or 'MG',
        'delivery_reference': customer.delivery_reference or '',
        'site_contact_name': customer.site_contact_name or '',
        'site_contact_phone': customer.site_contact_phone or customer.phone or '',
    })
