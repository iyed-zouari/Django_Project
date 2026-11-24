from django import forms

from ExpeditionApp.models import Expedition
from VehiculeApp.models import Vehicule
from .models import Offre


class OffreForm(forms.ModelForm):
    class Meta:
        model = Offre
        fields = ('expedition', 'vehicule', 'prix', 'delai_jours')
        widgets = {
            'prix': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'delai_jours': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, company, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.transporteur = company
        if self.instance.pk:
            del self.fields['expedition']
        else:
            self.fields['expedition'].queryset = Expedition.objects.filter(statut='publiee').order_by('reference')
        self.fields['vehicule'].queryset = Vehicule.objects.filter(
            entreprise=company, disponible=True,
        ).order_by('immatriculation')
