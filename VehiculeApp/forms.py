from django import forms

from EntrepriseApp.models import Entreprise

from .models import Vehicule


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ("immatriculation", "type_vehicule", "capacite_kg", "disponible", "entreprise")
        widgets = {
            "immatriculation": forms.TextInput(attrs={"placeholder": "Ex. 123 TUN 456"}),
            "capacite_kg": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["entreprise"].queryset = Entreprise.objects.filter(
            type_entreprise="transporteur"
        ).order_by("raison_sociale")
