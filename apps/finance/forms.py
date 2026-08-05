from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'value', 'description', 'date', 'due_date', 'paid_date', 'payment_status', 'payment_method']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().date().isoformat()
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'w-full px-4 py-2 border border-gray-300 rounded-lg '
                'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            )
