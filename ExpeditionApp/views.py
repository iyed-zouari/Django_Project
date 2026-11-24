from django.db.models import Exists, OuterRef, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.access import BusinessRoleMixin
from OffreApp.models import Offre
from .forms import ExpeditionForm
from .models import Expedition


class ExpeditionReadMixin(BusinessRoleMixin):
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    def get_queryset(self):
        offers = Offre.objects.filter(expedition_id=OuterRef('pk'))
        expeditions = Expedition.objects.select_related('entreprise').annotate(has_offers=Exists(offers))
        if self.company.type_entreprise == 'chargeur':
            return expeditions.filter(entreprise=self.company)
        sent_offers = offers.filter(transporteur=self.company)
        return expeditions.filter(Q(statut='publiee') | Exists(sent_offers))


class ExpeditionListView(ExpeditionReadMixin, ListView):
    template_name = 'expedition/list.html'
    context_object_name = 'liste'

    def get_queryset(self):
        return super().get_queryset().order_by('date_souhaitee', 'pk')


class ExpeditionDetailView(ExpeditionReadMixin, DetailView):
    template_name = 'expedition/detail.html'
    context_object_name = 'expedition'


class ChargeurMixin(BusinessRoleMixin):
    roles = ('chargeur',)


class EditableExpeditionMixin(ChargeurMixin):
    slug_field = 'reference'
    slug_url_kwarg = 'reference'

    def get_queryset(self):
        offers = Offre.objects.filter(expedition_id=OuterRef('pk'))
        return Expedition.objects.filter(entreprise=self.company, statut='publiee').filter(~Exists(offers))


class ExpeditionCreateView(ChargeurMixin, CreateView):
    model = Expedition
    form_class = ExpeditionForm
    template_name = 'expedition/forms.html'
    success_url = reverse_lazy('listview_expeditions')

    def form_valid(self, form):
        form.instance.entreprise = self.company
        return super().form_valid(form)


class ExpeditionUpdateView(EditableExpeditionMixin, UpdateView):
    form_class = ExpeditionForm
    template_name = 'expedition/forms.html'
    success_url = reverse_lazy('listview_expeditions')


class ExpeditionDeleteView(EditableExpeditionMixin, DeleteView):
    template_name = 'expedition/delete.html'
    success_url = reverse_lazy('listview_expeditions')
