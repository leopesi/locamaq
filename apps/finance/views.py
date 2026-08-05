from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from .models import Transaction
from .forms import TransactionForm


@login_required
def finance_dashboard(request):
    """Cash flow dashboard."""
    today = timezone.now().date()
    queryset = Transaction.objects.filter(tenant=request.tenant)

    # Date filter
    start_date = request.GET.get('start', today.replace(day=1).isoformat())
    end_date = request.GET.get('end', today.isoformat())

    filtered = queryset.filter(date__gte=start_date, date__lte=end_date)

    income = filtered.filter(type='income').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    expense = filtered.filter(type='expense').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    balance = income - expense

    # Pending
    pending = queryset.filter(type='income', payment_status='pending').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    overdue_count = queryset.filter(payment_status='overdue').count()

    transactions = filtered.order_by('-date', '-created_at')[:50]

    return render(request, 'finance/dashboard.html', {
        'transactions': transactions,
        'income': income,
        'expense': expense,
        'balance': balance,
        'pending': pending,
        'overdue_count': overdue_count,
        'start_date': start_date,
        'end_date': end_date,
    })


@login_required
def transaction_create(request):
    """Create a manual transaction."""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.tenant = request.tenant
            transaction.created_by = request.user
            transaction.save()
            messages.success(request, 'Transação registrada com sucesso.')
            return redirect('finance:dashboard')
    else:
        form = TransactionForm()
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': 'Nova Transação'})


@login_required
def transaction_edit(request, pk):
    """Edit an existing transaction."""
    transaction = get_object_or_404(Transaction, pk=pk, tenant=request.tenant)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada.')
            return redirect('finance:dashboard')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': f'Editar Transação'})


@login_required
def transaction_mark_paid(request, pk):
    """Mark a pending transaction as paid."""
    transaction = get_object_or_404(Transaction, pk=pk, tenant=request.tenant)
    today = timezone.now().date()
    transaction.payment_status = 'paid'
    transaction.paid_date = today
    transaction.save()

    # Se tem locação vinculada, marcar como paga também
    if transaction.rental:
        transaction.rental.is_paid = True
        transaction.rental.paid_at = today
        transaction.rental.save()

    messages.success(request, f'Transação marcada como paga (R$ {transaction.value}).')
    return redirect('finance:dashboard')
