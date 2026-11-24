from django import forms

from .models import Vehicule


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')
        widgets = {
            'immatriculation': forms.TextInput(attrs={'placeholder': 'Ex. 123 TUN 456'}),
            'capacite_kg': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        }
