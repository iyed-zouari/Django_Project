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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ('username', 'first_name', 'last_name', 'email', 'telephone')
        labels = {'email': 'Adresse Gmail', 'telephone': 'Téléphone'}
        widgets = {'telephone': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'})}


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label='Mot de passe actuel', strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError('Le mot de passe est incorrect.')
        return password
