from django import forms

from EntrepriseApp.models import Entreprise
from ExpeditionApp.models import Expedition
from VehiculeApp.models import Vehicule

from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ("expedition", "transporteur", "vehicule", "prix", "delai_jours", "statut")
        widgets = {
            "prix": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "delai_jours": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["transporteur"].queryset = Entreprise.objects.filter(
            type_entreprise="transporteur"
        ).order_by("raison_sociale")
        expeditions = Expedition.objects.filter(statut="publiee")
        if self.instance.pk:
            expeditions = expeditions | Expedition.objects.filter(pk=self.instance.expedition_id)
        self.fields["expedition"].queryset = expeditions.order_by("reference")
        vehicules = Vehicule.objects.filter(disponible=True)
        if self.instance.pk:
            vehicules = vehicules | Vehicule.objects.filter(pk=self.instance.vehicule_id)
        self.fields["vehicule"].queryset = vehicules.order_by("immatriculation")
