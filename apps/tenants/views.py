from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache

from apps.accounts.decorators import admin_required
from apps.inventory.models import Equipment
from apps.rentals.models import Rental
from apps.finance.models import Transaction
from apps.alerts.models import Notification
from apps.core.cache import tenant_cache_key, invalidate_tenant_cache
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from .forms import TenantSettingsForm, EvolutionAPIForm


def home(request):
    """Landing page for visitors, redirect to dashboard for logged users."""
    if request.user.is_authenticated:
        return redirect('tenants:dashboard')
    return render(request, 'landing.html')


@login_required
def guide(request):
    """Step-by-step onboarding guide."""
    return render(request, 'onboarding/guide.html')


@login_required
def dashboard(request):
    """Main dashboard view with real metrics. Cached per tenant (60s)."""
    tenant = request.tenant
    if not tenant:
        return render(request, 'dashboard.html', {})

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Cache stats for 60 seconds
    stats_key = tenant_cache_key(tenant.pk, 'dashboard_stats')
    stats = cache.get(stats_key)

    if not stats:
        stats = {
            'available_count': Equipment.objects.filter(tenant=tenant, state='available').count(),
            'rented_count': Equipment.objects.filter(tenant=tenant, state='rented').count(),
            'total_equipment': Equipment.objects.filter(tenant=tenant).count(),
            'active_rentals': Rental.objects.filter(tenant=tenant, status='active').count(),
            'overdue_rentals': Rental.objects.filter(
                tenant=tenant, status='active', expected_return__lt=today
            ).count(),
            'monthly_revenue': Transaction.objects.filter(
                tenant=tenant, type='income', date__gte=month_start, date__lte=today
            ).aggregate(total=Sum('value'))['total'] or Decimal('0.00'),
        }
        cache.set(stats_key, stats, 60)

    available_count = stats['available_count']
    rented_count = stats['rented_count']
    total_equipment = stats['total_equipment']
    active_rentals = stats['active_rentals']
    overdue_rentals = stats['overdue_rentals']
    monthly_revenue = stats['monthly_revenue']

    recent_rentals = Rental.objects.filter(tenant=tenant).select_related('customer').order_by('-created_at')[:5]

    # Map data — active rentals with coordinates
    map_rentals = Rental.objects.filter(
        tenant=tenant, status='active',
        delivery_lat__isnull=False, delivery_lng__isnull=False
    ).select_related('customer').prefetch_related('items__equipment')

    # Get rentals with notifications (overdue, payment pending)
    notified_rental_ids = set(
        Notification.objects.filter(
            tenant=tenant, status='unread', related_rental__isnull=False
        ).values_list('related_rental_id', flat=True)
    )

    map_markers = []
    for rental in map_rentals:
        equipments = ', '.join([item.equipment.name for item in rental.items.all()])
        has_alert = rental.pk in notified_rental_ids
        # Check overdue
        is_overdue = rental.expected_return < today

        map_markers.append({
            'lat': float(rental.delivery_lat),
            'lng': float(rental.delivery_lng),
            'title': f'#{rental.pk} - {rental.customer.name}',
            'address': rental.delivery_address,
            'equipments': equipments,
            'id': rental.pk,
            'has_alert': has_alert,
            'is_overdue': is_overdue,
            'alert_text': 'ATRASADA' if is_overdue else ('PAGAMENTO PENDENTE' if has_alert else ''),
            'distance_km': float(rental.delivery_distance_km) if rental.delivery_distance_km else None,
            'time_min': rental.delivery_time_min,
        })

    import json

    # Notifications
    recent_notifications = Notification.objects.filter(
        tenant=tenant, status='unread'
    ).order_by('-created_at')[:5]
    unread_count = Notification.objects.filter(tenant=tenant, status='unread').count()

    return render(request, 'dashboard.html', {
        'available_count': available_count,
        'rented_count': rented_count,
        'total_equipment': total_equipment,
        'active_rentals': active_rentals,
        'overdue_rentals': overdue_rentals,
        'monthly_revenue': monthly_revenue,
        'recent_rentals': recent_rentals,
        'map_markers_json': json.dumps(map_markers),
        'recent_notifications': recent_notifications,
        'unread_count': unread_count,
    })


@login_required
@admin_required
def settings_general(request):
    """Tenant general settings (company info, contract clauses)."""
    tenant = request.tenant
    if request.method == 'POST':
        form = TenantSettingsForm(request.POST, request.FILES, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso.')
            return redirect('tenants:settings_general')
    else:
        form = TenantSettingsForm(instance=tenant)
    return render(request, 'settings/general.html', {'form': form})


@login_required
@admin_required
def settings_whatsapp(request):
    """Evolution API (WhatsApp) settings."""
    tenant = request.tenant
    if request.method == 'POST':
        form = EvolutionAPIForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações do WhatsApp salvas.')
            return redirect('tenants:settings_whatsapp')
    else:
        form = EvolutionAPIForm(instance=tenant)

    # Test connection
    connection_status = None
    if request.GET.get('test') == '1' and tenant.evolution_api_url:
        try:
            from apps.notifications.services import EvolutionAPIService
            service = EvolutionAPIService(
                base_url=tenant.evolution_api_url,
                api_key=tenant.evolution_api_key,
                instance=tenant.evolution_instance,
            )
            result = service.check_connection()
            connection_status = {'ok': True, 'data': str(result)}
        except Exception as e:
            connection_status = {'ok': False, 'error': str(e)}

    return render(request, 'settings/whatsapp.html', {
        'form': form,
        'connection_status': connection_status,
    })
