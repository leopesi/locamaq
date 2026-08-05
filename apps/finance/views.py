from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
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

    transactions = filtered.order_by('-date', '-created_at')[:50]

    return render(request, 'finance/dashboard.html', {
        'transactions': transactions,
        'income': income,
        'expense': expense,
        'balance': balance,
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
