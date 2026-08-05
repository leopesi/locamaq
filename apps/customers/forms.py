from django import forms
from .models import Customer


INPUT_CLASS = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            # Identificação
            'person_type', 'name', 'trade_name', 'document', 'rg',
            # Contato
            'phone', 'phone2', 'whatsapp', 'email',
            # Endereço
            'zip_code', 'address', 'number', 'complement', 'neighborhood', 'city', 'state',
            # Entrega
            'delivery_address', 'delivery_number', 'delivery_neighborhood',
            'delivery_city', 'delivery_state', 'delivery_reference',
            # Contato na obra
            'site_contact_name', 'site_contact_phone',
            # Referências
            'reference1_name', 'reference1_phone', 'reference2_name', 'reference2_phone',
            # Financeiro
            'credit_limit', 'payment_terms',
            # Observações
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 3,
                    'class': INPUT_CLASS,
                })
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = INPUT_CLASS
            else:
                field.widget.attrs['class'] = INPUT_CLASS

        # Placeholders
        self.fields['document'].widget.attrs['placeholder'] = '000.000.000-00 ou 00.000.000/0001-00'
        self.fields['zip_code'].widget.attrs['placeholder'] = '00000-000'
        self.fields['whatsapp'].widget.attrs['placeholder'] = '(11) 99999-9999'
        self.fields['phone'].widget.attrs['placeholder'] = '(11) 99999-9999'
        self.fields['payment_terms'].widget.attrs['placeholder'] = 'Ex: À vista, 30 dias'
        self.fields['credit_limit'].widget.attrs['placeholder'] = '0.00'
