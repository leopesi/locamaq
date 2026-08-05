from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.rentals.models import Rental
from apps.notifications.services import EvolutionAPIService


@login_required
def send_receipt_whatsapp(request, rental_id):
    """Send rental receipt via WhatsApp to customer."""
    rental = get_object_or_404(Rental, pk=rental_id, tenant=request.tenant)
    customer = rental.customer

    if not customer.whatsapp:
        messages.error(request, 'Cliente não possui WhatsApp cadastrado.')
        return redirect('rentals:rental_detail', pk=rental.pk)

    if request.method == 'POST':
        try:
            service = EvolutionAPIService.from_tenant(request.tenant)

            # Send text notification
            text = (
                f'🏗️ *COMPROVANTE DE LOCAÇÃO*\n\n'
                f'📋 Locação #{rental.pk}\n'
                f'📅 Período: {rental.start_date.strftime("%d/%m/%Y")} → {rental.expected_return.strftime("%d/%m/%Y")}\n'
                f'💰 Valor: R$ {rental.total_value}\n\n'
                f'Equipamentos:\n'
            )
            for item in rental.items.select_related('equipment').all():
                text += f'  • {item.equipment.name} (x{item.quantity})\n'
            text += f'\n{request.tenant.name}'

            service.send_text(customer.whatsapp, text)

            # Send PDF
            pdf_url = request.build_absolute_uri(f'/documents/rental/{rental.pk}/pdf/')
            service.send_media(customer.whatsapp, pdf_url, caption='Comprovante de Locação')

            messages.success(request, f'Comprovante enviado via WhatsApp para {customer.whatsapp}.')
        except Exception as e:
            messages.error(request, f'Erro ao enviar WhatsApp: {str(e)}')

        return redirect('rentals:rental_detail', pk=rental.pk)

    return render(request, 'notifications/confirm_send.html', {
        'rental': rental,
        'customer': customer,
    })


@login_required
def send_notification(request, rental_id):
    """Send a custom notification to customer."""
    rental = get_object_or_404(Rental, pk=rental_id, tenant=request.tenant)
    customer = rental.customer

    if request.method == 'POST':
        message = request.POST.get('message', '')
        if not message:
            messages.error(request, 'Mensagem não pode ser vazia.')
            return redirect('rentals:rental_detail', pk=rental.pk)

        if not customer.whatsapp:
            messages.error(request, 'Cliente não possui WhatsApp cadastrado.')
            return redirect('rentals:rental_detail', pk=rental.pk)

        try:
            service = EvolutionAPIService.from_tenant(request.tenant)
            service.send_text(customer.whatsapp, message)
            messages.success(request, f'Mensagem enviada para {customer.name}.')
        except Exception as e:
            messages.error(request, f'Erro ao enviar: {str(e)}')

        return redirect('rentals:rental_detail', pk=rental.pk)

    return render(request, 'notifications/send_message.html', {
        'rental': rental,
        'customer': customer,
    })
