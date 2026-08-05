from django import forms
from .models import Tenant


INPUT_CLASS = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
)


class TenantSettingsForm(forms.ModelForm):
    """Form for tenant general settings."""
    class Meta:
        model = Tenant
        fields = [
            'name', 'document', 'phone', 'email', 'address', 'logo',
            'contract_clauses', 'return_conditions', 'penalty_terms',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'rows': 4, 'class': INPUT_CLASS})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full'
            else:
                field.widget.attrs['class'] = INPUT_CLASS


class EvolutionAPIForm(forms.ModelForm):
    """Form for Evolution API (WhatsApp) settings."""
    class Meta:
        model = Tenant
        fields = ['evolution_api_url', 'evolution_api_key', 'evolution_instance']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_CLASS

        self.fields['evolution_api_url'].widget.attrs['placeholder'] = 'http://localhost:8080 ou https://evolution.seudominio.com'
        self.fields['evolution_api_key'].widget.attrs['placeholder'] = 'Sua API Key'
        self.fields['evolution_instance'].widget.attrs['placeholder'] = 'Nome da instância (ex: locamaq)'
