from django import forms
from .models import AlertRule


INPUT_CLASS = (
    'w-full px-4 py-2 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
)


class AlertRuleForm(forms.ModelForm):
    class Meta:
        model = AlertRule
        fields = ['alert_type', 'severity', 'is_active', 'notify_channel', 'threshold', 'notify_phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'h-5 w-5 text-blue-600 rounded'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = INPUT_CLASS
            else:
                field.widget.attrs['class'] = INPUT_CLASS

        self.fields['threshold'].widget.attrs['placeholder'] = 'Ex: 3 dias, 5 unidades, 5000 reais'
        self.fields['notify_phone'].widget.attrs['placeholder'] = '5511999999999'
