from django import forms

from .models import Product
from .utils import generate_part_number


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'part_number': forms.TextInput({'value': generate_part_number()})
        }
