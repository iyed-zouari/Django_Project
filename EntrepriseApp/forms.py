from django import forms
from .models import Entreprise, Utilisateur


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ("raison_sociale", "matricule_fiscal", "adresse", "type_entreprise", "gerant")
        widgets = {"adresse": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gerants = Utilisateur.objects.filter(entreprise__isnull=True)
        if self.instance.pk:
            gerants = gerants | Utilisateur.objects.filter(pk=self.instance.gerant_id)
        self.fields["gerant"].queryset = gerants.order_by("username")
