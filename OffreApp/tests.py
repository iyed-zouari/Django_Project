from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from EntrepriseApp.models import Utilisateur, Entreprise
from VehiculeApp.models import Vehicule
from ExpeditionApp.models import Expedition
from OffreApp.models import Offre


class TransConnectModelsTestCase(TestCase):
    def setUp(self):
        # Création des utilisateurs
        self.user_chargeur = Utilisateur.objects.create_user(
            username='user_chargeur',
            email='chargeur@gmail.com',
            password='Password123!',
            role='chargeur'
        )
        self.user_transporteur1 = Utilisateur.objects.create_user(
            username='user_transporteur1',
            email='transporteur1@gmail.com',
            password='Password123!',
            role='transporteur'
        )
        self.user_transporteur2 = Utilisateur.objects.create_user(
            username='user_transporteur2',
            email='transporteur2@gmail.com',
            password='Password123!',
            role='transporteur'
        )

        # Création des entreprises
        self.entreprise_chargeur = Entreprise.objects.create(
            raison_sociale='Société Industrielle Nord',
            matricule_fiscal='1234567AAM000',
            adresse='123 Rue de la République, 1001 Tunis',
            type_entreprise='chargeur',
            gerant=self.user_chargeur
        )

        self.entreprise_transporteur1 = Entreprise.objects.create(
            raison_sociale='Express Fret SARL',
            matricule_fiscal='7654321-B-B-M-000',
            adresse='45 Avenue Habib Bourguiba, 2000 Le Bardo',
            type_entreprise='transporteur',
            gerant=self.user_transporteur1
        )

        self.entreprise_transporteur2 = Entreprise.objects.create(
            raison_sociale='LogiTrans Tunisie',
            matricule_fiscal='9876543/C/D/M/000',
            adresse='89 Rue des Entrepreneurs, Z.I Charguia',
            type_entreprise='transporteur',
            gerant=self.user_transporteur2
        )

        # Création des véhicules pour transporteur 1
        self.vehicule_camionnette = Vehicule.objects.create(
            immatriculation='111-TUN-100',
            type_vehicule='camionnette',
            capacite_kg=Decimal('1200.00'),
            disponible=True,
            entreprise=self.entreprise_transporteur1
        )

        self.vehicule_fourgon = Vehicule.objects.create(
            immatriculation='111-TUN-200',
            type_vehicule='fourgon',
            capacite_kg=Decimal('3000.00'),
            disponible=True,
            entreprise=self.entreprise_transporteur1
        )

        self.vehicule_porteur = Vehicule.objects.create(
            immatriculation='111-TUN-300',
            type_vehicule='camion_porteur',
            capacite_kg=Decimal('15000.00'),
            disponible=True,
            entreprise=self.entreprise_transporteur1
        )

        self.vehicule_semi = Vehicule.objects.create(
            immatriculation='111-TUN-400',
            type_vehicule='semi_remorque',
            capacite_kg=Decimal('25000.00'),
            disponible=True,
            entreprise=self.entreprise_transporteur1
        )

        # Véhicule indisponible
        self.vehicule_indisponible = Vehicule.objects.create(
            immatriculation='111-TUN-500',
            type_vehicule='fourgon',
            capacite_kg=Decimal('2500.00'),
            disponible=False,
            entreprise=self.entreprise_transporteur1
        )

        # Véhicule pour transporteur 2
        self.vehicule_trans2 = Vehicule.objects.create(
            immatriculation='222-TUN-100',
            type_vehicule='fourgon',
            capacite_kg=Decimal('2500.00'),
            disponible=True,
            entreprise=self.entreprise_transporteur2
        )

    # -------------------------------------------------------------
    # SECTION III : CONTRAINTES DE MODÉLISATION
    # -------------------------------------------------------------
    def test_utilisateur_user_id_generation(self):
        """Format AAuserNN avec les 2 derniers chiffres de l'année."""
        annee = timezone.now().strftime("%y")
        self.assertTrue(self.user_chargeur.user_id.startswith(f"{annee}user"))
        self.assertEqual(len(self.user_chargeur.user_id), 8)

    def test_utilisateur_email_gmail_only(self):
        """Seuls les emails gmail.com sont acceptés."""
        user = Utilisateur(
            username='test_invalid_email',
            email='test@yahoo.com',
            role='chargeur'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_entreprise_matricule_fiscal_regex(self):
        """Le matricule fiscal tunisien doit respecter le regex."""
        # Matricule invalide
        ent_bad = Entreprise(
            raison_sociale='Bad Ent',
            matricule_fiscal='ABC',
            adresse='123 Rue de la République, 1001 Tunis',
            type_entreprise='chargeur',
            gerant=self.user_chargeur
        )
        with self.assertRaises(ValidationError):
            ent_bad.full_clean()

    def test_entreprise_adresse_longueur_minimale(self):
        """L'adresse doit comporter au moins 20 caractères."""
        ent = Entreprise(
            raison_sociale='Test Ent',
            matricule_fiscal='1234567AAM000',
            adresse='Court',
            type_entreprise='chargeur',
            gerant=self.user_chargeur
        )
        with self.assertRaises(ValidationError):
            ent.full_clean()

    def test_vehicule_capacite_nulle_refusee(self):
        """Une capacité nulle ou négative ne peut pas être acceptée."""
        veh = Vehicule(
            immatriculation='999-TUN-000',
            type_vehicule='camionnette',
            capacite_kg=Decimal('0.00'),
            entreprise=self.entreprise_transporteur1
        )
        with self.assertRaises(ValidationError):
            veh.full_clean()

    def test_vehicule_entreprise_doit_etre_transporteur(self):
        """Un véhicule doit être rattaché à une entreprise de type transporteur."""
        veh = Vehicule(
            immatriculation='999-TUN-001',
            type_vehicule='camionnette',
            capacite_kg=Decimal('1000.00'),
            entreprise=self.entreprise_chargeur  # Erreur : chargeur
        )
        with self.assertRaises(ValidationError):
            veh.full_clean()

    def test_expedition_reference_generation(self):
        """Format EXP-AA-NNNNN généré automatiquement."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('800.00'),
            entreprise=self.entreprise_chargeur
        )
        annee = timezone.now().strftime("%y")
        self.assertTrue(exp.reference.startswith(f"EXP-{annee}-"))
        self.assertEqual(len(exp.reference), 12)

    def test_expedition_poids_nul_refuse(self):
        """Le poids ne peut pas être nul ou négatif."""
        exp = Expedition(
            ville_depart='Tunis',
            ville_arrivee='Sfax',
            poids_kg=Decimal('0.00'),
            entreprise=self.entreprise_chargeur
        )
        with self.assertRaises(ValidationError):
            exp.full_clean()

    def test_expedition_entreprise_doit_etre_chargeur(self):
        """L'entreprise associée à l'expédition doit être de type chargeur."""
        exp = Expedition(
            ville_depart='Tunis',
            ville_arrivee='Bizerte',
            poids_kg=Decimal('500.00'),
            entreprise=self.entreprise_transporteur1  # Erreur : transporteur
        )
        with self.assertRaises(ValidationError):
            exp.full_clean()

    def test_offre_prix_et_delai_validateurs(self):
        """prix > 0 et delai_jours >= 1."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Nabeul',
            poids_kg=Decimal('500.00'),
            entreprise=self.entreprise_chargeur
        )
        # Prix nul
        offre_prix_nul = Offre(
            prix=Decimal('0.00'),
            delai_jours=2,
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_camionnette
        )
        with self.assertRaises(ValidationError):
            offre_prix_nul.full_clean()

        # Délai inférieur à 1
        offre_delai_invalide = Offre(
            prix=Decimal('150.00'),
            delai_jours=0,
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_camionnette
        )
        with self.assertRaises(ValidationError):
            offre_delai_invalide.full_clean()

    # -------------------------------------------------------------
    # SECTION IV : RÈGLES MÉTIER À IMPLÉMENTER
    # -------------------------------------------------------------
    def test_regle_1_offre_par_transporteur_uniquement(self):
        """1. Une offre ne peut être créée que par une entreprise dont type_entreprise = transporteur."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Gabès',
            poids_kg=Decimal('500.00'),
            entreprise=self.entreprise_chargeur
        )
        offre = Offre(
            prix=Decimal('300.00'),
            delai_jours=2,
            expedition=exp,
            transporteur=self.entreprise_chargeur,  # Chargeur au lieu de transporteur
            vehicule=self.vehicule_camionnette
        )
        with self.assertRaises(ValidationError):
            offre.full_clean()

    def test_regle_2_vehicule_meme_transporteur(self):
        """2. Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('1000.00'),
            entreprise=self.entreprise_chargeur
        )
        offre = Offre(
            prix=Decimal('200.00'),
            delai_jours=1,
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_trans2  # Véhicule de transporteur 2 !
        )
        with self.assertRaises(ValidationError):
            offre.full_clean()

    def test_regle_3_expedition_statut_publiee_pour_nouvelles_offres(self):
        """3. Une expédition ne peut recevoir de nouvelles offres que si son statut est publiee."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('1000.00'),
            statut='en_cours',  # Pas au statut 'publiee'
            entreprise=self.entreprise_chargeur
        )
        offre = Offre(
            prix=Decimal('200.00'),
            delai_jours=1,
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_camionnette
        )
        with self.assertRaises(ValidationError):
            offre.full_clean()

    def test_regle_4_pas_deux_offres_proposee_actives_par_entreprise(self):
        """4. Une entreprise ne peut pas avoir deux offres proposee actives sur la même expédition."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('1000.00'),
            entreprise=self.entreprise_chargeur
        )
        # Première offre
        Offre.objects.create(
            prix=Decimal('200.00'),
            delai_jours=1,
            statut='proposee',
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_camionnette
        )
        # Deuxième offre proposee par la même entreprise sur la même expédition
        offre2 = Offre(
            prix=Decimal('180.00'),
            delai_jours=1,
            statut='proposee',
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_fourgon
        )
        with self.assertRaises(ValidationError):
            offre2.full_clean()

    def test_regle_5_cascade_acceptation(self):
        """5. Cascade à l'acceptation : expédition -> attribuee, autres offres proposee -> refusee."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sousse',
            poids_kg=Decimal('1000.00'),
            entreprise=self.entreprise_chargeur
        )
        offre1 = Offre.objects.create(
            prix=Decimal('200.00'),
            delai_jours=1,
            statut='proposee',
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_camionnette
        )
        offre2 = Offre.objects.create(
            prix=Decimal('250.00'),
            delai_jours=2,
            statut='proposee',
            expedition=exp,
            transporteur=self.entreprise_transporteur2,
            vehicule=self.vehicule_trans2
        )

        # Acceptation de offre1
        offre1.statut = 'acceptee'
        offre1.save()

        # Vérifications en base
        exp.refresh_from_db()
        offre2.refresh_from_db()

        self.assertEqual(exp.statut, 'attribuee')
        self.assertEqual(offre2.statut, 'refusee')

    def test_regle_6_vehicule_non_disponible_refuse(self):
        """6. Un véhicule dont disponible = False ne peut pas être proposé sur une nouvelle offre."""
        exp = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sfax',
            poids_kg=Decimal('1000.00'),
            entreprise=self.entreprise_chargeur
        )
        offre = Offre(
            prix=Decimal('200.00'),
            delai_jours=1,
            expedition=exp,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_indisponible  # disponible = False
        )
        with self.assertRaises(ValidationError):
            offre.full_clean()

    def test_regle_7_compatibilite_type_vehicule_et_poids(self):
        """7. Compatibilité entre type_vehicule et poids de l'expédition."""
        # Cas Camionnette : jusqu'à 1500 kg
        exp_lourde_pour_camionnette = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sfax',
            poids_kg=Decimal('2000.00'),  # > 1500 kg
            entreprise=self.entreprise_chargeur
        )
        offre_bad_camionnette = Offre(
            prix=Decimal('200.00'),
            delai_jours=1,
            expedition=exp_lourde_pour_camionnette,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_camionnette
        )
        with self.assertRaises(ValidationError):
            offre_bad_camionnette.full_clean()

        # Cas Fourgon : jusqu'à 3500 kg
        exp_lourde_pour_fourgon = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sfax',
            poids_kg=Decimal('5000.00'),  # > 3500 kg
            entreprise=self.entreprise_chargeur
        )
        offre_bad_fourgon = Offre(
            prix=Decimal('400.00'),
            delai_jours=1,
            expedition=exp_lourde_pour_fourgon,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_fourgon
        )
        with self.assertRaises(ValidationError):
            offre_bad_fourgon.full_clean()

        # Cas Camion Porteur : ~3,5 à 19 t
        offre_good_porteur = Offre(
            prix=Decimal('600.00'),
            delai_jours=1,
            expedition=exp_lourde_pour_fourgon,  # 5000 kg est bien dans 3500 - 19000 kg
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_porteur
        )
        # Doit passer sans erreur
        offre_good_porteur.full_clean()

        # Cas Camion Porteur dépassé (> 19t)
        exp_tres_lourde = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sfax',
            poids_kg=Decimal('22000.00'),  # 22 t > 19 t
            entreprise=self.entreprise_chargeur
        )
        offre_bad_porteur = Offre(
            prix=Decimal('1000.00'),
            delai_jours=1,
            expedition=exp_tres_lourde,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_porteur
        )
        with self.assertRaises(ValidationError):
            offre_bad_porteur.full_clean()

        # Cas Semi-remorque : ~19 à 26 t
        offre_good_semi = Offre(
            prix=Decimal('1200.00'),
            delai_jours=1,
            expedition=exp_tres_lourde,  # 22 t est bien dans 19 - 26 t
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_semi
        )
        # Doit passer sans erreur
        offre_good_semi.full_clean()

        # Cas Semi-remorque dépassé (> 26t)
        exp_hors_norme = Expedition.objects.create(
            ville_depart='Tunis',
            ville_arrivee='Sfax',
            poids_kg=Decimal('30000.00'),  # 30 t > 26 t
            entreprise=self.entreprise_chargeur
        )
        offre_bad_semi = Offre(
            prix=Decimal('1500.00'),
            delai_jours=1,
            expedition=exp_hors_norme,
            transporteur=self.entreprise_transporteur1,
            vehicule=self.vehicule_semi
        )
        with self.assertRaises(ValidationError):
            offre_bad_semi.full_clean()
