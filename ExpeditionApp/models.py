from datetime import datetime

from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Expedition(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids = models.DecimalField(validators=[MinValueValidator(0,"Le poids doit être un nombre positif.")], max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('publiee', 'publiee'), ('attribuee', 'attribuee'), ('en_cours', 'en_cours'),('livree','livree'),('annulee','annulee')], default='publiee')
    entreprise = models.ForeignKey('EntrepriseApp.Entreprise', on_delete=models.CASCADE, related_name='expeditions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

def clean(self):
    super().clean()
    if self.entreprise_id and self.entreprise_.type_entreprise != 'c':
        raise ValidationError("L'entreprise associée à l'expédition doit être de type 'c' (Chargeur).")

    @classmethod
    def _generate_reference(cls):
        annee=datetime.now().strftime("%Y")
        prefix = f"EXP_{annee}_"
        last_expedition = cls.objects.filter(reference__startswith=prefix).order_by('reference').last()
        if last_expedition:
            last_reference = last_expedition.reference
            last_number = int(last_reference.split('_')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        if new_number > 99999:
            raise ValidationError(
                "Le nombre d'expéditions a atteint la limite maximale pour cette année."
            )
        return f"{prefix}{new_number:05d}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()  # Validate the model before saving
        super().save(*args, **kwargs)
        

    