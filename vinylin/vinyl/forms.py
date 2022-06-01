from django import forms
from django.contrib.admin.sites import site
from django.contrib.admin.widgets import (
    AutocompleteSelect,
    AutocompleteSelectMultiple,
)

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Vinyl, Artist, Genre, Country
from store.utils import generate_part_number


class VinylAdminForm(forms.ModelForm):
    overview = forms.CharField(widget=CKEditorUploadingWidget())
    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        widget=AutocompleteSelect(Vinyl._meta.get_field('artist'), site)
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=AutocompleteSelectMultiple(
            Vinyl._meta.get_field('genres'),
            site
        )
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=AutocompleteSelect(Vinyl._meta.get_field('country'), site)
    )

    class Meta:
        model = Vinyl
        fields = '__all__'
        widgets = {
            'part_number': forms.TextInput({'value': generate_part_number()})
        }
