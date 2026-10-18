
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
        validators=[
            MinValueValidator(
                Decimal('0.01'),
                "Le prix doit être strictement supérieur à 0."
            )
        ]
    )

    delai_jours = models.IntegerField(
        validators=[
            MinValueValidator(
                1,
                "Le délai doit être supérieur ou égal à 1 jour."
            )
        ]
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

        # 1. Vérifier que l'entreprise est un transporteur
        if (
            self.transporteur_id
            and self.transporteur.type_entreprise != 'transporteur'
        ):
            raise ValidationError({
                'transporteur': "Seul un transporteur peut créer une offre."
            })

        # 2. Vérifier que le véhicule appartient au transporteur
        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                    'vehicule': "Le véhicule doit appartenir au transporteur."
                })

        # 3. Une nouvelle offre exige une expédition publiée
        if not self.pk and self.expedition_id:
            if self.expedition.statut != 'publiee':
                raise ValidationError({
                    'expedition': "L'expédition doit être publiée."
                })

        # 4. Empêcher deux offres proposées du même transporteur
        #    pour la même expédition
        if (
            self.statut == 'proposee'
            and self.expedition_id
            and self.transporteur_id
        ):
            offres = Offre.objects.filter(
                expedition_id=self.expedition_id,
                transporteur_id=self.transporteur_id,
                statut='proposee'
            )

            if self.pk:
                offres = offres.exclude(pk=self.pk)

            if offres.exists():
                raise ValidationError(
                    "Ce transporteur possède déjà une offre proposée "
                    "pour cette expédition."
                )

        # 5. Un nouveau véhicule doit être disponible
        if not self.pk and self.vehicule_id:
            if not self.vehicule.disponible:
                raise ValidationError({
                    'vehicule': "Le véhicule n'est pas disponible."
                })

        # 6. Vérifier la capacité et le type du véhicule
        if self.vehicule_id and self.expedition_id:
            poids = self.expedition.poids_kg
            vehicule = self.vehicule

            if poids is not None:
                if (
                    vehicule.capacite_kg is not None
                    and poids > vehicule.capacite_kg
                ):
                    raise ValidationError({
                        'vehicule': "Le poids dépasse la capacité du véhicule."
                    })

                type_vehicule = vehicule.type_vehicule

                limites = {
                    'camionnette': (0, 1500),
                    'fourgon': (0, 3500),
                    'camion_porteur': (3500, 19000),
                    'semi_remorque': (19000, 26000),
                }

                if type_vehicule in limites:
                    minimum, maximum = limites[type_vehicule]

                    if poids > maximum or (
                        minimum > 0 and poids < minimum
                    ):
                        raise ValidationError({
                            'vehicule': (
                                "Le poids de l'expédition est incompatible "
                                "avec le type de véhicule."
                            )
                        })

    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():
            ancien_statut = None

            if self.pk:
                ancien_statut = (
                    Offre.objects
                    .filter(pk=self.pk)
                    .values_list('statut', flat=True)
                    .first()
                )

            super().save(*args, **kwargs)

            # Traiter uniquement le passage au statut acceptée
            if (
                self.statut == 'acceptee'
                and ancien_statut != 'acceptee'
            ):
                expedition = self.expedition
                expedition.statut = 'attribuee'
                expedition.save(update_fields=['statut'])

                Offre.objects.filter(
                    expedition_id=self.expedition_id,
                    statut='proposee'
                ).exclude(pk=self.pk).update(statut='refusee')

    def __str__(self):
        return (
            f"Offre #{self.pk} - {self.prix} TND "
            f"({self.get_statut_display()})"
        )
