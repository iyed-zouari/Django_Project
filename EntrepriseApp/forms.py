from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Entreprise, Utilisateur


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(label='Rôle', choices=(
        ('chargeur', 'Chargeur'), ('transporteur', 'Transporteur'),
    ))

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ('username', 'email', 'role')
        labels = {'email': 'Adresse Gmail'}


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ('raison_sociale', 'matricule_fiscal', 'adresse')
        widgets = {'adresse': forms.Textarea(attrs={'rows': 4})}
