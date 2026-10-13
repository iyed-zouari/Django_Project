from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from ExpeditionApp.models import Expedition
from EntrepriseApp.models import Entreprise
from VehiculeApp.models import Vehicule


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ]

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), "Le prix doit être strictement supérieur à 0.")]
    )
    delai_jours = models.IntegerField(
        validators=[MinValueValidator(1, "Le délai doit être supérieur ou égal à 1 jour.")]
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='proposee'
    )
    date_proposition = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        related_name='offres'
    )
    transporteur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='offres'
    )
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.CASCADE,
        related_name='offres'
    )

    def clean(self):
        super().clean()

        # Section III : Validateurs champs
        if self.prix is not None and self.prix <= 0:
            raise ValidationError({
                'prix': "Le prix doit être strictement supérieur à 0."
            })

        if self.delai_jours is not None and self.delai_jours < 1:
            raise ValidationError({
                'delai_jours': "Le délai doit être supérieur ou égal à 1 jour."
            })

        # Section IV - Règle 1 :
        # Une offre ne peut être créée que par une entreprise dont type_entreprise = transporteur.
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({
                'transporteur': "Une offre ne peut être créée que par une entreprise dont type_entreprise = transporteur."
            })

        # Section IV - Règle 2 :
        # Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur de l'offre.
        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                    'vehicule': "Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur de l'offre."
                })

        # Section IV - Règle 3 :
        # Une expédition ne peut recevoir de nouvelles offres que si son statut est publiee.
        if not self.pk and self.expedition_id:
            statut_exp = getattr(self.expedition, 'statut', None) or getattr(self.expedition, 'status', None)
            if statut_exp != 'publiee':
                raise ValidationError({
                    'expedition': "Une expédition ne peut recevoir de nouvelles offres que si son statut est 'publiee'."
                })

        # Section IV - Règle 4 :
        # Une entreprise ne peut pas avoir deux offres au statut proposee actives simultanément sur la même expédition.
        if self.statut == 'proposee' and self.expedition_id and self.transporteur_id:
            qs = Offre.objects.filter(
                expedition_id=self.expedition_id,
                transporteur_id=self.transporteur_id,
                statut='proposee'
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    "Une entreprise ne peut pas avoir deux offres au statut proposee actives simultanément sur la même expédition."
                )

        # Section IV - Règle 6 :
        # Un véhicule dont disponible = False ne peut pas être proposé sur une nouvelle offre.
        if not self.pk and self.vehicule_id and not self.vehicule.disponible:
            raise ValidationError({
                'vehicule': "Un véhicule dont disponible = False ne peut pas être proposé sur une nouvelle offre."
            })

        # Section IV - Règle 7 :
        # L'attribut type_vehicule conditionne la compatibilité avec le poids d'une expédition.
        # - camionnette : Jusqu’à ~1,5 t (1500 kg)
        # - fourgon : ~3,5 t (3500 kg)
        # - camion_porteur : ~3,5 à 19 t (3500 à 19000 kg)
        # - semi_remorque : ~19 à 26 t (19000 à 26000 kg)
        if self.vehicule_id and self.expedition_id:
            poids = getattr(self.expedition, 'poids_kg', None)
            if poids is None:
                poids = getattr(self.expedition, 'poids', None)

            if poids is not None:
                type_veh = self.vehicule.type_vehicule

                # Capacité physique propre au véhicule
                if self.vehicule.capacite_kg and poids > self.vehicule.capacite_kg:
                    raise ValidationError({
                        'vehicule': f"Le poids de l'expédition ({poids} kg) dépasse la capacité maximale du véhicule ({self.vehicule.capacite_kg} kg)."
                    })

                # Compatibilité par catégorie de véhicule
                if type_veh == 'camionnette' and poids > 1500:
                    raise ValidationError({
                        'vehicule': f"Une camionnette ne peut transporter qu'une charge jusqu'à 1,5 t (1500 kg). Poids demandé: {poids} kg."
                    })
                elif type_veh == 'fourgon' and poids > 3500:
                    raise ValidationError({
                        'vehicule': f"Un fourgon ne peut transporter qu'une charge jusqu'à 3,5 t (3500 kg). Poids demandé: {poids} kg."
                    })
                elif type_veh == 'camion_porteur' and (poids < 3500 or poids > 19000):
                    raise ValidationError({
                        'vehicule': f"Un camion porteur est adapté aux expéditions de 3,5 à 19 t (3500 à 19000 kg). Poids demandé: {poids} kg."
                    })
                elif type_veh == 'semi_remorque' and (poids < 19000 or poids > 26000):
                    raise ValidationError({
                        'vehicule': f"Une semi-remorque est adaptée aux expéditions de 19 à 26 t (19000 à 26000 kg). Poids demandé: {poids} kg."
                    })

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)

            # Section IV - Règle 5 :
            # Cascade à l'acceptation : quand une offre passe au statut « acceptee »,
            # l'expédition associée passe automatiquement à « attribuee »,
            # et toutes les autres offres « proposee » sur cette même expédition passent automatiquement à « refusee ».
            if self.statut == 'acceptee':
                exp = self.expedition
                exp_statut = getattr(exp, 'statut', None) or getattr(exp, 'status', None)
                if exp_statut != 'attribuee':
                    if hasattr(exp, 'statut'):
                        exp.statut = 'attribuee'
                    if hasattr(exp, 'status'):
                        exp.status = 'attribuee'
                    exp.save()

                Offre.objects.filter(
                    expedition_id=self.expedition_id,
                    statut='proposee'
                ).exclude(pk=self.pk).update(statut='refusee')

    def __str__(self):
        return f"Offre #{self.pk or ''} - {self.prix} TND ({self.get_statut_display()})"
