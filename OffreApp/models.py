from django.db import models
from ExpeditionApp.models import Expedition
from EntrepriseApp.models import Entreprise
from VehiculeApp.models import Vehicule

STATUT_CHOICES = [
    ('proposee', 'Proposée'),
    ('acceptee', 'Acceptée'),
    ('refusee', 'Refusée'),
    ('retiree', 'Retirée'),
]
# Create your models here.
class Offre(models.Model):
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours = models.IntegerField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='proposee'
    )
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE)
    transporteur = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, null=True,blank=True)
