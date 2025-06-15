from django import forms
from .models import Cabana

class CabanaForm(forms.ModelForm):
    class Meta:
        model = Cabana
        fields = ['nombre', 'ubicacion', 'capacidad', 'estado']
