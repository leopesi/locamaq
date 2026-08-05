from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from apps.accounts.decorators import admin_required
from .models import AlertRule, Notification
from .forms import AlertRuleForm
from .engine import AlertEngine


@login_required
def notification_list(request):
    """List notifications for current user/tenant."""
    notifications = Notification.objects.filter(tenant=request.tenant)

    severity_filter = request.GET.get('severity', '')
    status_filter = request.GET.get('status', '')

    if severity_filter:
        notifications = notifications.filter(severity=severity_filter)
    if status_filter:
        notifications = notifications.filter(status=status_filter)
    else:
        notifications = notifications.exclude(status='dismissed')

    return render(request, 'alerts/notification_list.html', {
        'notifications': notifications[:50],
        'unread_count': Notification.objects.filter(tenant=request.tenant, status='unread').count(),
        'severity_filter': severity_filter,
        'status_filter': status_filter,
    })


@login_required
def notification_mark_read(request, pk):
    """Mark a notification as read."""
    notif = get_object_or_404(Notification, pk=pk, tenant=request.tenant)
    notif.status = 'read'
    notif.read_at = timezone.now()
    notif.save()
    return redirect('alerts:notification_list')


@login_required
def notification_dismiss(request, pk):
    """Dismiss a notification."""
    notif = get_object_or_404(Notification, pk=pk, tenant=request.tenant)
    notif.status = 'dismissed'
    notif.save()
    return redirect('alerts:notification_list')


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(tenant=request.tenant, status='unread').update(
        status='read', read_at=timezone.now()
    )
    messages.success(request, 'Todas notificações marcadas como lidas.')
    return redirect('alerts:notification_list')


@login_required
@admin_required
def alert_setup(request):
    """Alert rules setup panel."""
    rules = AlertRule.objects.filter(tenant=request.tenant)
    return render(request, 'alerts/setup.html', {'rules': rules})


@login_required
@admin_required
def alert_rule_create(request):
    """Create a new alert rule."""
    if request.method == 'POST':
        form = AlertRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.tenant = request.tenant
            rule.save()
            messages.success(request, f'Regra de alerta criada: {rule.get_alert_type_display()}')
            return redirect('alerts:setup')
    else:
        form = AlertRuleForm()
    return render(request, 'alerts/rule_form.html', {'form': form, 'title': 'Nova Regra de Alerta'})


@login_required
@admin_required
def alert_rule_edit(request, pk):
    """Edit an alert rule."""
    rule = get_object_or_404(AlertRule, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        form = AlertRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, f'Regra atualizada: {rule.get_alert_type_display()}')
            return redirect('alerts:setup')
    else:
        form = AlertRuleForm(instance=rule)
    return render(request, 'alerts/rule_form.html', {'form': form, 'title': f'Editar: {rule.get_alert_type_display()}'})


@login_required
@admin_required
def alert_rule_delete(request, pk):
    """Delete an alert rule."""
    rule = get_object_or_404(AlertRule, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        rule.delete()
        messages.success(request, 'Regra de alerta removida.')
        return redirect('alerts:setup')
    return render(request, 'alerts/rule_confirm_delete.html', {'rule': rule})


@login_required
@admin_required
def alert_run_checks(request):
    """Manually trigger alert checks."""
    engine = AlertEngine(request.tenant)
    results = engine.run_all_checks()
    if results:
        messages.success(request, f'{len(results)} nova(s) notificação(ões) gerada(s).')
    else:
        messages.info(request, 'Nenhuma nova notificação. Tudo em ordem! ✅')
    return redirect('alerts:notification_list')
