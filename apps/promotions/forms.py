from django import forms
from .models import Promotion


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['title', 'message', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 5,
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                    'placeholder': 'Escreva a mensagem da promoção...',
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full'
            else:
                field.widget.attrs['class'] = (
                    'w-full px-4 py-2 border border-gray-300 rounded-lg '
                    'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                )
