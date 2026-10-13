from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Vehicule(models.Model):
    TYPE_VEHICULE_CHOICES = [
        ('camionnette', 'Camionnette / utilitaire léger'),
        ('camion_porteur', 'Camion porteur'),
        ('semi_remorque', 'Semi-remorque'),
        ('fourgon', 'Fourgon'),
    ]

    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(
        max_length=50,
        choices=TYPE_VEHICULE_CHOICES
    )
    capacite_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), "La capacité doit être strictement positive.")]
    )
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='vehicules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # Normalisation du type de véhicule si nécessaire
        if self.type_vehicule:
            normalized = self.type_vehicule.replace('-', '_').replace(' ', '_').strip(',').lower()
            valid_keys = dict(self.TYPE_VEHICULE_CHOICES).keys()
            if normalized in valid_keys:
                self.type_vehicule = normalized

        # Section III : Une capacité nulle ne peut pas être acceptée
        if self.capacite_kg is not None and self.capacite_kg <= 0:
            raise ValidationError({
                'capacite_kg': "Une capacité nulle ne peut pas être acceptée."
            })

        # Section III : entreprise doit être de type transporteur (règle métier)
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({
                'entreprise': "Un véhicule ne peut être rattaché qu'à une entreprise de type transporteur."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_vehicule_display()} ({self.immatriculation})"