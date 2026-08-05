from django import forms
from .models import Rental, RentalItem
from apps.customers.models import Customer
from apps.inventory.models import Equipment


INPUT_CLASS = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
)


class RentalForm(forms.ModelForm):
    """Main rental form with inline equipment selection."""

    # Equipamentos (até 10 itens inline)
    equipment_1 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 1')
    qty_1 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_1 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_2 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 2')
    qty_2 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_2 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_3 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 3')
    qty_3 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_3 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_4 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 4')
    qty_4 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_4 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_5 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 5')
    qty_5 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_5 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_6 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 6')
    qty_6 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_6 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_7 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 7')
    qty_7 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_7 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_8 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 8')
    qty_8 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_8 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_9 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 9')
    qty_9 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_9 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    equipment_10 = forms.ModelChoiceField(queryset=Equipment.objects.none(), required=False, label='Equipamento 10')
    qty_10 = forms.IntegerField(min_value=1, initial=1, required=False, label='Qtd')
    value_10 = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Valor Unit.')

    # Endereço de entrega (obrigatórios)
    delivery_address = forms.CharField(max_length=300, required=True, label='Endereço de Entrega *')
    delivery_reference = forms.CharField(max_length=200, required=False, label='Ponto de Referência')
    delivery_contact = forms.CharField(max_length=200, required=True, label='Responsável no Local *')
    delivery_phone = forms.CharField(max_length=20, required=True, label='Telefone do Responsável *')

    class Meta:
        model = Rental
        fields = ['customer', 'period_type', 'start_date', 'expected_return', 'payment_method', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_return': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, tenant, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant

        # Pre-set today's date
        from django.utils import timezone
        today = timezone.now().date().isoformat()
        if not self.initial.get('start_date'):
            self.initial['start_date'] = today

        self.fields['customer'].queryset = Customer.objects.filter(
            tenant=tenant, is_active=True, is_blocked=False
        ).order_by('name')

        available_equipment = Equipment.objects.filter(tenant=tenant, state='available').order_by('code')
        for i in range(1, 11):
            self.fields[f'equipment_{i}'].queryset = available_equipment

        # Apply styling
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'rows': 3, 'class': INPUT_CLASS})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = INPUT_CLASS
            else:
                field.widget.attrs['class'] = INPUT_CLASS

        # Placeholders
        for i in range(1, 11):
            self.fields[f'value_{i}'].widget.attrs['placeholder'] = '0 = tabela'
            self.fields[f'qty_{i}'].widget.attrs['placeholder'] = '1'

        self.fields['delivery_address'].widget.attrs['placeholder'] = 'Rua, número - Bairro, Cidade/UF'
        self.fields['delivery_reference'].widget.attrs['placeholder'] = 'Próximo a...'
        self.fields['delivery_contact'].widget.attrs['placeholder'] = 'Nome do responsável na obra'
        self.fields['delivery_phone'].widget.attrs['placeholder'] = '(34) 9 9999-9999'

    def clean(self):
        cleaned_data = super().clean()
        # Validate at least 1 equipment selected
        has_equipment = False
        for i in range(1, 11):
            if cleaned_data.get(f'equipment_{i}'):
                has_equipment = True
                break
        if not has_equipment:
            raise forms.ValidationError('Selecione pelo menos 1 equipamento.')
        return cleaned_data

    def get_items(self):
        """Return list of (equipment, quantity, unit_value) tuples."""
        items = []
        for i in range(1, 11):
            equipment = self.cleaned_data.get(f'equipment_{i}')
            if equipment:
                qty = self.cleaned_data.get(f'qty_{i}') or 1
                value = self.cleaned_data.get(f'value_{i}') or None
                items.append((equipment, qty, value))
        return items


class RentalItemForm(forms.ModelForm):
    """Form for adding individual items (used on add-item page)."""
    class Meta:
        model = RentalItem
        fields = ['equipment', 'quantity', 'unit_value']

    def __init__(self, tenant, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment'].queryset = Equipment.objects.filter(
            tenant=tenant, state='available'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_CLASS


class RentalEditForm(forms.ModelForm):
    """Form for editing an existing rental (general data only)."""
    class Meta:
        model = Rental
        fields = [
            'customer', 'period_type', 'start_date', 'expected_return',
            'payment_method', 'is_paid', 'paid_at',
            'delivery_address', 'delivery_reference', 'delivery_contact', 'delivery_phone',
            'notes',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_return': forms.DateInput(attrs={'type': 'date'}),
            'paid_at': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, tenant, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(
            tenant=tenant, is_active=True
        ).order_by('name')
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'rows': 3, 'class': INPUT_CLASS})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-5 w-5 text-blue-600 rounded'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = INPUT_CLASS
            else:
                field.widget.attrs['class'] = INPUT_CLASS


class RentalReturnForm(forms.Form):
    actual_return = forms.DateField(
        label='Data de Devolução',
        widget=forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS})
    )
    notes = forms.CharField(
        label='Observações',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': INPUT_CLASS})
    )
