from django.test import Client, TestCase
from django.urls import reverse

from ExpeditionApp.models import Expedition
from OffreApp.models import Offre
from VehiculeApp.models import Vehicule
from .models import Entreprise, Utilisateur


class AccountTests(TestCase):
    def setUp(self):
        self.signup = {
            'username': 'nouveau', 'email': 'nouveau@gmail.com', 'role': 'transporteur',
            'password1': 'Entreposage-91!Tunisie', 'password2': 'Entreposage-91!Tunisie',
        }

    def test_register_company_login_and_logout(self):
        self.assertContains(self.client.get(reverse('home')), 'Créer un compte')
        self.assertContains(self.client.get(reverse('register')), 'Créer mon compte')
        company_url = reverse('entreprise_create')
        self.assertRedirects(self.client.post(reverse('register'), self.signup), company_url)
        user = Utilisateur.objects.get(username='nouveau')
        self.assertEqual(user.role, 'transporteur')
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password(self.signup['password1']))
        self.assertRedirects(self.client.get(reverse('vehicule_list')), company_url)
        self.assertEqual(self.client.post(reverse('vehicule_create'), {}).status_code, 403)
        response = self.client.post(company_url, {
            'raison_sociale': 'Mon Transport', 'matricule_fiscal': '1234567/A/A/M/001',
            'adresse': '123 avenue des ateliers de Tunis', 'type_entreprise': 'chargeur',
            'gerant': 'identifiant-forge',
        })
        self.assertRedirects(response, reverse('entreprise_list'))
        company = Entreprise.objects.get(gerant=user)
        self.assertEqual(company.type_entreprise, 'transporteur')
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.client.post(reverse('login'), {
            'username': user.username, 'password': self.signup['password1'],
            'next': reverse('vehicule_list'),
        }), reverse('vehicule_list'))

    def test_registration_rejects_admin_and_non_gmail(self):
        response = self.client.post(reverse('register'), {**self.signup, 'role': 'admin'})
        self.assertIn('role', response.context['form'].errors)
        response = self.client.post(reverse('register'), {**self.signup, 'email': 'nouveau@example.org'})
        self.assertIn('email', response.context['form'].errors)
        self.assertFalse(Utilisateur.objects.exists())


class LogisticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chargeur, cls.company = cls.make_company('chargeur1', 'chargeur', 1)
        cls.autre_chargeur, cls.other_company = cls.make_company('chargeur2', 'chargeur', 2)
        cls.transporteur, cls.carrier = cls.make_company('transport1', 'transporteur', 3)
        cls.autre_transporteur, cls.other_carrier = cls.make_company('transport2', 'transporteur', 4)
        cls.vehicle = cls.make_vehicle('123 TUN 456', cls.carrier)
        cls.other_vehicle = cls.make_vehicle('234 TUN 456', cls.other_carrier)
        cls.private_expedition = Expedition.objects.create(
            entreprise=cls.other_company, ville_depart='Tozeur', ville_arrivee='Tunis', statut='livree',
        )

    @staticmethod
    def make_company(name, role, serial):
        user = Utilisateur.objects.create_user(username=name, email=f'{name}@gmail.com', role=role)
        company = Entreprise.objects.create(
            raison_sociale=name, matricule_fiscal=f'{serial:07d}/A/A/M/001',
            adresse='123 avenue des ateliers de Tunis', type_entreprise=role, gerant=user,
        )
        return user, company

    @staticmethod
    def make_vehicle(registration, company):
        return Vehicule.objects.create(
            immatriculation=registration, entreprise=company, type_vehicule='fourgon', capacite_kg=900,
        )

    def publish(self):
        self.client.force_login(self.chargeur)
        response = self.client.post(reverse('createview_expedition'), {
            'ville_depart': 'Sfax', 'ville_arrivee': 'Tunis', 'poids_kg': '300',
            'date_souhaitee': '2027-02-05', 'entreprise': self.other_company.pk, 'statut': 'livree',
        })
        self.assertRedirects(response, reverse('listview_expeditions'))
        expedition = Expedition.objects.get(ville_depart='Sfax')
        self.assertEqual(expedition.entreprise, self.company)
        self.assertEqual(expedition.statut, 'publiee')
        return expedition

    def offer_data(self, expedition, vehicle):
        return {'expedition': expedition.pk, 'vehicule': vehicle.pk, 'prix': '125.00', 'delai_jours': '1'}

    def offer_for(self, expedition, carrier, vehicle):
        return Offre.objects.create(expedition=expedition, transporteur=carrier, vehicule=vehicle, prix=125, delai_jours=1)

    def test_full_offer_workflow(self):
        expedition = self.publish()
        self.client.force_login(self.transporteur)
        self.assertContains(self.client.get(reverse('listview_expeditions')), expedition.reference)
        self.assertNotContains(self.client.get(reverse('listview_expeditions')), self.private_expedition.reference)
        self.assertContains(self.client.get(reverse('detailview_expedition', args=[expedition.pk])), 'Proposer une offre')
        response = self.client.post(reverse('offre_create'), {
            **self.offer_data(expedition, self.vehicle), 'statut': 'acceptee', 'transporteur': self.other_carrier.pk,
        })
        self.assertRedirects(response, reverse('offre_list'))
        offer = Offre.objects.get()
        self.assertEqual(offer.statut, 'proposee')
        self.assertEqual(offer.transporteur, self.carrier)
        update_url = reverse('offre_update', args=[offer.pk])
        self.assertContains(self.client.get(update_url), 'Modifier l’offre')
        self.assertRedirects(self.client.post(update_url, {
            **self.offer_data(self.private_expedition, self.vehicle), 'prix': '150.00', 'statut': 'acceptee',
        }), reverse('offre_list'))
        offer.refresh_from_db()
        self.assertEqual(offer.expedition, expedition)
        self.assertEqual(offer.statut, 'proposee')
        self.assertEqual(offer.prix, 150)
        competitor = self.offer_for(expedition, self.other_carrier, self.other_vehicle)

        accept_url = reverse('offre_accept', args=[offer.pk])
        self.client.force_login(self.chargeur)
        self.assertContains(self.client.get(reverse('offre_detail', args=[offer.pk])), 'Accepter cette offre')
        self.assertEqual(self.client.get(accept_url).status_code, 405)
        self.assertRedirects(self.client.post(accept_url), reverse('offre_detail', args=[offer.pk]))
        self.client.post(reverse('offre_accept', args=[competitor.pk]))
        expedition.refresh_from_db()
        offer.refresh_from_db()
        competitor.refresh_from_db()
        self.assertEqual(expedition.statut, 'attribuee')
        self.assertEqual(offer.statut, 'acceptee')
        self.assertEqual(competitor.statut, 'refusee')
        self.client.force_login(self.transporteur)
        self.assertEqual(self.client.get(update_url).status_code, 404)

    def test_business_access_is_scoped(self):
        self.assertRedirects(self.client.get(reverse('offre_list')), reverse('login') + '?next=/offres/')
        expedition = self.publish()
        offer = self.offer_for(expedition, self.carrier, self.vehicle)
        self.client.force_login(self.autre_chargeur)
        self.assertEqual(self.client.get(reverse('detailview_expedition', args=[expedition.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('offre_accept', args=[offer.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('vehicule_list')).status_code, 403)
        self.assertEqual(self.client.get(reverse('offre_create')).status_code, 403)
        self.assertEqual(self.client.get(reverse('entreprise_detail', args=[self.company.pk])).status_code, 404)
        self.client.force_login(self.autre_transporteur)
        self.assertEqual(self.client.get(reverse('vehicule_update', args=[self.vehicle.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('offre_detail', args=[offer.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('offre_accept', args=[offer.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('updateview_expedition', args=[expedition.pk]), {}).status_code, 403)
        response = self.client.post(reverse('offre_create'), self.offer_data(expedition, self.vehicle))
        self.assertIn('vehicule', response.context['form'].errors)
        self.assertEqual(Offre.objects.count(), 1)

    def test_deletion_requires_post_and_acceptance_requires_csrf(self):
        expedition = self.publish()
        delete_url = reverse('delete_expedition', args=[expedition.reference])
        self.assertContains(self.client.get(delete_url), expedition.reference)
        self.assertTrue(Expedition.objects.filter(pk=expedition.pk).exists())
        offer = self.offer_for(expedition, self.carrier, self.vehicle)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.chargeur)
        self.assertEqual(csrf_client.post(reverse('offre_accept', args=[offer.pk])).status_code, 403)
        self.assertEqual(self.client.delete(delete_url).status_code, 405)
        self.assertEqual(self.client.post(delete_url).status_code, 404)
        offer.refresh_from_db()
        self.assertEqual(offer.statut, 'proposee')

    def test_acceptance_rechecks_vehicle_availability(self):
        expedition = self.publish()
        offer = self.offer_for(expedition, self.carrier, self.vehicle)
        Vehicule.objects.filter(pk=self.vehicle.pk).update(disponible=False)
        response = self.client.post(reverse('offre_accept', args=[offer.pk]), follow=True)
        self.assertContains(response, 'n’est plus disponible')
        offer.refresh_from_db()
        self.assertEqual(offer.statut, 'proposee')

    def test_vehicle_crud_keeps_company_ownership(self):
        self.client.force_login(self.transporteur)
        response = self.client.post(reverse('vehicule_create'), {
            'immatriculation': '444 TUN 555', 'type_vehicule': 'fourgon', 'capacite_kg': '1800',
            'disponible': 'on', 'entreprise': self.other_carrier.pk,
        })
        self.assertRedirects(response, reverse('vehicule_list'))
        vehicle = Vehicule.objects.get(immatriculation='444 TUN 555')
        self.assertEqual(vehicle.entreprise, self.carrier)
        self.assertNotContains(self.client.get(reverse('vehicule_list')), self.other_vehicle.immatriculation)
        self.assertContains(self.client.get(reverse('vehicule_detail', args=[vehicle.pk])), vehicle.immatriculation)
        delete_url = reverse('vehicule_delete', args=[vehicle.pk])
        self.assertEqual(self.client.delete(delete_url).status_code, 405)
        self.assertRedirects(self.client.post(delete_url), reverse('vehicule_list'))
        self.assertFalse(Vehicule.objects.filter(pk=vehicle.pk).exists())


class ProfileTests(TestCase):
    password = 'Mot-De-Passe-42!'

    @classmethod
    def setUpTestData(cls):
        cls.user = Utilisateur.objects.create_user(
            username='profil', email='profil@gmail.com', password=cls.password, role='transporteur',
        )
        cls.other_user = Utilisateur.objects.create_user(username='autre', email='autre@gmail.com')

    def setUp(self):
        self.profile_url = reverse('profile')
        self.delete_url = reverse('delete_account')

    def test_profile_and_delete_require_login(self):
        for url in (self.profile_url, self.delete_url):
            for method in (self.client.get, self.client.post):
                self.assertRedirects(method(url), f'{reverse("login")}?next={url}')

    def test_update_only_updates_own_profile_and_allowed_fields(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.get(self.profile_url), 'Mon profil')
        response = self.client.post(self.profile_url, {
            'username': 'nouveauprofil', 'first_name': 'Nour', 'last_name': 'Amari',
            'email': 'nouveauprofil@gmail.com', 'telephone': '55123456',
            'user_id': self.other_user.pk, 'role': 'admin', 'is_staff': 'on', 'is_superuser': 'on',
        })
        self.assertRedirects(response, self.profile_url)
        self.user.refresh_from_db()
        self.other_user.refresh_from_db()
        self.assertEqual(self.user.username, 'nouveauprofil')
        self.assertEqual(self.user.first_name, 'Nour')
        self.assertEqual(self.user.last_name, 'Amari')
        self.assertEqual(self.user.email, 'nouveauprofil@gmail.com')
        self.assertEqual(self.user.telephone, '55123456')
        self.assertEqual(self.user.role, 'transporteur')
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(self.other_user.username, 'autre')
        self.assertEqual(self.client.session['_auth_user_id'], self.user.pk)

    def test_profile_rejects_duplicate_email(self):
        self.client.force_login(self.user)
        response = self.client.post(self.profile_url, {'username': self.user.username, 'email': self.other_user.email})
        self.assertIn('email', response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'profil@gmail.com')

    def test_delete_requires_password_and_signs_out(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.get(self.delete_url), 'Confirmer la suppression')
        self.assertTrue(Utilisateur.objects.filter(pk=self.user.pk).exists())
        self.assertEqual(self.client.delete(self.delete_url).status_code, 405)
        response = self.client.post(self.delete_url, {'password': 'incorrect'})
        self.assertContains(response, 'Le mot de passe est incorrect.')
        self.assertTrue(Utilisateur.objects.filter(pk=self.user.pk).exists())
        response = self.client.post(self.delete_url, {'password': self.password}, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, 'Votre compte a été supprimé.')
        self.assertFalse(Utilisateur.objects.filter(pk=self.user.pk).exists())
        self.assertTrue(Utilisateur.objects.filter(pk=self.other_user.pk).exists())
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_delete_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.delete_url, {'password': self.password}).status_code, 403)
        self.assertTrue(Utilisateur.objects.filter(pk=self.user.pk).exists())

    def test_active_shipment_blocks_carrier_deletion_until_completed(self):
        carrier = Entreprise.objects.create(
            gerant=self.user, type_entreprise='transporteur', raison_sociale='Société de transport',
            adresse='123 avenue des ateliers de Tunis', matricule_fiscal='0000001/A/A/M/001',
        )
        sender = Entreprise.objects.create(
            gerant=self.other_user, type_entreprise='chargeur', raison_sociale='Société de distribution',
            adresse='456 avenue des ateliers de Tunis', matricule_fiscal='0000002/A/A/M/001',
        )
        vehicle = LogisticsTests.make_vehicle('333 TUN 555', carrier)
        shipment = Expedition.objects.create(entreprise=sender, ville_depart='Sfax', ville_arrivee='Tunis')
        offer = Offre.objects.create(
            expedition=shipment, transporteur=carrier, vehicule=vehicle, prix=100, delai_jours=1, statut='acceptee',
        )
        self.client.force_login(self.user)
        response = self.client.post(self.delete_url, {'password': self.password})
        self.assertContains(response, 'La suppression est bloquée')
        self.assertTrue(Utilisateur.objects.filter(pk=self.user.pk).exists())
        self.assertTrue(Offre.objects.filter(pk=offer.pk).exists())
        Expedition.objects.filter(pk=shipment.pk).update(statut='livree')
        self.assertRedirects(self.client.post(self.delete_url, {'password': self.password}), reverse('home'))
        self.assertFalse(Entreprise.objects.filter(pk=carrier.pk).exists())
        self.assertFalse(Vehicule.objects.filter(pk=vehicle.pk).exists())
        self.assertFalse(Offre.objects.filter(pk=offer.pk).exists())
        self.assertTrue(Expedition.objects.filter(pk=shipment.pk, statut='livree').exists())
