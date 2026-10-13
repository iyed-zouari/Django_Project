from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_gmail(value):
    if not value:
        raise ValidationError("L'adresse e-mail ne peut pas être vide.")
    if not value.lower().endswith('@gmail.com'):
        raise ValidationError("Seuls les emails appartenant au domaine gmail.com sont acceptés.")


# Alias de compatibilité pour les migrations existantes
validate_email = validate_gmail


matricule_validator = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="Format du matricule fiscal invalide."
)

user_id_validator = RegexValidator(
    regex=r'^\d{2}user\d{2}$',
    message="Le user_id doit respecter le format AAuserNN (ex: 26user00)."
)


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur'),
    ]

    user_id = models.CharField(
        primary_key=True,
        max_length=8,
        unique=True,
        validators=[user_id_validator]
    )
    email = models.EmailField(unique=True, validators=[validate_gmail])
    telephone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='chargeur')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def generate_user_id(cls, year=None):
        """
        Structure format : AAuserNN
        - AA : 2 derniers chiffres de l'année d'inscription (ex. 26 pour 2026)
        - user : constante fixe
        - NN : compteur séquentiel 00-99, remis à zéro chaque année
        """
        if year is None:
            annee = timezone.now().strftime("%y")
        else:
            annee = str(year)[-2:]
        prefix = f"{annee}user"
        existing_ids = cls.objects.filter(user_id__startswith=prefix).values_list('user_id', flat=True)
        numbers = []
        for uid in existing_ids:
            if len(uid) == 8 and uid[6:].isdigit():
                numbers.append(int(uid[6:]))
        next_num = (max(numbers) + 1) if numbers else 0
        if next_num > 99:
            raise ValidationError(
                "Le nombre d'utilisateurs a atteint la limite maximale pour cette année (99)."
            )
        return f"{prefix}{next_num:02d}"

    def clean(self):
        super().clean()
        if self.email and not self.email.lower().endswith('@gmail.com'):
            raise ValidationError({'email': "Seuls les emails appartenant au domaine gmail.com sont acceptés."})

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.generate_user_id()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.user_id})"


class Entreprise(models.Model):
    TYPE_CHOICES = [
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur'),
    ]

    raison_sociale = models.CharField(max_length=200, blank=False, null=False)
    matricule_fiscal = models.CharField(
        max_length=17,
        unique=True,
        validators=[matricule_validator],
        db_column='matricule_fiscale'
    )
    adresse = models.TextField(
        validators=[
            MinLengthValidator(20, "L'adresse doit contenir au moins 20 caractères."),
            MaxLengthValidator(400, "L'adresse ne peut pas dépasser 400 caractères.")
        ],
        blank=False,
        null=False
    )
    type_entreprise = models.CharField(
        max_length=100,
        choices=TYPE_CHOICES,
        default='chargeur'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='entreprise'
    )

    @property
    def matricule_fiscale(self):
        return self.matricule_fiscal

    @matricule_fiscale.setter
    def matricule_fiscale(self, value):
        self.matricule_fiscal = value

    def clean(self):
        super().clean()
        # Normalisation si 'c' ou 't' est passé
        if self.type_entreprise == 'c':
            self.type_entreprise = 'chargeur'
        elif self.type_entreprise == 't':
            self.type_entreprise = 'transporteur'

        if self.adresse and len(self.adresse.strip()) < 20:
            raise ValidationError({'adresse': "L'adresse doit contenir au moins 20 caractères."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.raison_sociale} ({self.get_type_entreprise_display()})"