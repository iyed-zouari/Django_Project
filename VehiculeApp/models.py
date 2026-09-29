from django.db import models

# Create your models here.
class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=20, unique=True)
    type_vehicule = models.CharField(max_length=50, choices=[('camionnette,', 'camionnette,'), ('camion porteur,', 'camion porteur,'),('semi-remorque','semi-remorque'), ('fourgon', 'Fourgon')])
    capacite_kg = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    entreprise = models.ForeignKey('EntrepriseApp.Entreprise', on_delete=models.CASCADE, related_name='vehicules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)