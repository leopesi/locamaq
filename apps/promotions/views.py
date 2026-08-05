from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Promotion
from .forms import PromotionForm
from apps.customers.models import Customer
from apps.accounts.decorators import admin_required
from apps.notifications.services import EvolutionAPIService


@login_required
@admin_required
def promotion_list(request):
    """List all promotions."""
    promotions = Promotion.objects.filter(tenant=request.tenant)
    return render(request, 'promotions/promotion_list.html', {'promotions': promotions})


@login_required
@admin_required
def promotion_create(request):
    """Create a new promotion."""
    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES)
        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.tenant = request.tenant
            promotion.created_by = request.user
            promotion.save()
            messages.success(request, f'Promoção "{promotion.title}" criada. Agora envie para os clientes.')
            return redirect('promotions:promotion_send', pk=promotion.pk)
    else:
        form = PromotionForm()
    return render(request, 'promotions/promotion_form.html', {'form': form, 'title': 'Nova Promoção'})


@login_required
@admin_required
def promotion_send(request, pk):
    """Send promotion to selected customers."""
    promotion = get_object_or_404(Promotion, pk=pk, tenant=request.tenant)
    customers = Customer.objects.filter(tenant=request.tenant, is_active=True).exclude(whatsapp='')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('customers')
        if not selected_ids:
            messages.error(request, 'Selecione pelo menos um cliente.')
            return redirect('promotions:promotion_send', pk=pk)

        selected_customers = customers.filter(pk__in=selected_ids)
        sent_count = 0
        errors = 0

        service = EvolutionAPIService.from_tenant(request.tenant)

        for customer in selected_customers:
            try:
                service.send_text(customer.whatsapp, promotion.message)
                sent_count += 1
            except Exception:
                errors += 1

        promotion.sent_at = timezone.now()
        promotion.recipients_count = sent_count
        promotion.save()

        msg = f'Promoção enviada para {sent_count} cliente(s).'
        if errors:
            msg += f' ({errors} falha(s))'
        messages.success(request, msg)
        return redirect('promotions:promotion_list')

    return render(request, 'promotions/promotion_send.html', {
        'promotion': promotion,
        'customers': customers,
    })
