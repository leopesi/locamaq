from django import forms
from .models import Equipment


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'code', 'name', 'description', 'category', 'state',
            'daily_rate', 'weekly_rate', 'monthly_rate', 'image', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 3,
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full'
            else:
                field.widget.attrs['class'] = (
                    'w-full px-4 py-2 border border-gray-300 rounded-lg '
                    'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                )
