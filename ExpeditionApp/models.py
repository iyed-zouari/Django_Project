from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

reference_validator = RegexValidator(
    regex=r'^EXP-\d{2}-\d{5}$',
    message="La référence doit respecter le format EXP-AA-NNNNN (ex: EXP-26-00001)."
)


class Expedition(models.Model):
    STATUT_CHOICES = [
        ('publiee', 'Publiée'),
        ('attribuee', 'Attribuée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    reference = models.CharField(
        max_length=100,
        unique=True,
        validators=[reference_validator]
    )
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0.01'), "Le poids doit être strictement positif.")]
    )
    date_souhaitee = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='publiee'
    )
    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='expeditions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def poids(self):
        return self.poids_kg

    @poids.setter
    def poids(self, value):
        self.poids_kg = value

    @property
    def status(self):
        return self.statut

    @status.setter
    def status(self, value):
        self.statut = value

    @classmethod
    def generate_reference(cls, year=None):
        """
        Structure format : EXP-AA-NNNNN
        - EXP : constante fixe
        - AA : 2 derniers chiffres de l'année de création
        - NNNNN : compteur séquentiel 00001–99999, remis à zéro chaque année
        """
        if year is None:
            annee = timezone.now().strftime("%y")
        else:
            annee = str(year)[-2:]
        prefix = f"EXP-{annee}-"
        existing_refs = cls.objects.filter(reference__startswith=prefix).values_list('reference', flat=True)
        numbers = []
        for ref in existing_refs:
            parts = ref.split('-')
            if len(parts) == 3 and parts[-1].isdigit():
                numbers.append(int(parts[-1]))
        next_num = (max(numbers) + 1) if numbers else 1
        if next_num > 99999:
            raise ValidationError(
                "Le nombre d'expéditions a atteint la limite maximale pour cette année (99999)."
            )
        return f"{prefix}{next_num:05d}"

    def clean(self):
        super().clean()
        # Section III : Ne pas accepter un poids nul
        if self.poids_kg is not None and self.poids_kg <= 0:
            raise ValidationError({
                'poids_kg': "Ne pas accepter un poids nul ou négatif."
            })

        # Section III : Doit être de type chargeur (règle métier)
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({
                'entreprise': "L'entreprise associée à l'expédition doit être de type chargeur."
            })

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} ({self.ville_depart} -> {self.ville_arrivee})"