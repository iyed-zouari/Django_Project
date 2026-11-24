from django.contrib import messages
from django.db.models import Exists, OuterRef
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.access import BusinessRoleMixin
from OffreApp.models import Offre
from .forms import VehiculeForm
from .models import Vehicule


class TransporteurMixin(BusinessRoleMixin):
    roles = ('transporteur',)


class OwnedVehicleMixin(TransporteurMixin):
    def get_queryset(self):
        offers = Offre.objects.filter(vehicule_id=OuterRef('pk'))
        return Vehicule.objects.filter(entreprise=self.company).annotate(has_offers=Exists(offers))


class VehiculeListView(OwnedVehicleMixin, ListView):
    template_name = 'vehicule/list.html'
    context_object_name = 'vehicules'

    def get_queryset(self):
        return super().get_queryset().order_by('immatriculation')


class VehiculeDetailView(OwnedVehicleMixin, DetailView):
    template_name = 'vehicule/detail.html'
    context_object_name = 'vehicule'


class VehiculeCreateView(TransporteurMixin, CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'vehicule/form.html'
    success_url = reverse_lazy('vehicule_list')

    def form_valid(self, form):
        form.instance.entreprise = self.company
        return super().form_valid(form)


class VehiculeUpdateView(OwnedVehicleMixin, UpdateView):
    form_class = VehiculeForm
    template_name = 'vehicule/form.html'
    success_url = reverse_lazy('vehicule_list')


class VehiculeDeleteView(OwnedVehicleMixin, DeleteView):
    template_name = 'vehicule/delete.html'
    context_object_name = 'vehicule'
    success_url = reverse_lazy('vehicule_list')

    def form_valid(self, form):
        if self.object.offres.exists():
            messages.error(self.request, 'Ce véhicule est lié à une offre. Vous pouvez le rendre indisponible.')
            return self.form_invalid(form)
        return super().form_valid(form)
