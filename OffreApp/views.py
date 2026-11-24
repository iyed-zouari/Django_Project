from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.access import BusinessRoleMixin, company_for
from ExpeditionApp.models import Expedition
from .forms import OffreForm
from .models import Offre


class VisibleOffresMixin(BusinessRoleMixin):
    def get_queryset(self):
        offers = Offre.objects.select_related('expedition', 'transporteur', 'vehicule')
        if self.company.type_entreprise == 'chargeur':
            return offers.filter(expedition__entreprise=self.company)
        return offers.filter(transporteur=self.company)


class OffreListView(VisibleOffresMixin, ListView):
    template_name = 'offre/list.html'
    context_object_name = 'offres'

    def get_queryset(self):
        offers = super().get_queryset().order_by('-created_at', '-pk')
        if self.request.GET.get('expedition'):
            offers = offers.filter(expedition__reference=self.request.GET['expedition'])
        return offers


class OffreDetailView(VisibleOffresMixin, DetailView):
    template_name = 'offre/detail.html'
    context_object_name = 'offre'


class EditableOffresMixin(VisibleOffresMixin):
    roles = ('transporteur',)

    def get_queryset(self):
        return super().get_queryset().filter(statut='proposee', expedition__statut='publiee')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        expedition_id = self.get_object().expedition_id
        # Même ordre de verrouillage que pour l’acceptation d’une offre.
        get_object_or_404(Expedition.objects.select_for_update(), pk=expedition_id, statut='publiee')
        return super().post(request, *args, **kwargs)


class OffreFormMixin:
    form_class = OffreForm
    template_name = 'offre/form.html'
    success_url = reverse_lazy('offre_list')

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'company': self.company}

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as exc:
            form.add_error(None, exc.messages)
            return self.form_invalid(form)


class OffreCreateView(OffreFormMixin, BusinessRoleMixin, CreateView):
    roles = ('transporteur',)
    model = Offre

    def get_initial(self):
        return {**super().get_initial(), 'expedition': self.request.GET.get('expedition')}

    @transaction.atomic
    def form_valid(self, form):
        expedition = get_object_or_404(Expedition.objects.select_for_update(), pk=form.instance.expedition_id)
        if expedition.statut != 'publiee':
            form.add_error('expedition', 'Cette expédition n’est plus ouverte aux offres.')
            return self.form_invalid(form)
        form.instance.expedition = expedition
        return super().form_valid(form)


class OffreUpdateView(EditableOffresMixin, OffreFormMixin, UpdateView):
    pass


class OffreDeleteView(EditableOffresMixin, DeleteView):
    template_name = 'offre/delete.html'
    context_object_name = 'offre'
    success_url = reverse_lazy('offre_list')


@login_required
@require_POST
@transaction.atomic
def accept_offer(request, pk):
    company = company_for(request.user)
    if not company or request.user.role != 'chargeur':
        raise PermissionDenied

    candidate = get_object_or_404(Offre.objects.filter(expedition__entreprise=company), pk=pk)
    expedition = get_object_or_404(Expedition.objects.select_for_update(), pk=candidate.expedition_id)
    offer = get_object_or_404(Offre.objects.select_related('vehicule'), pk=pk, expedition=expedition)
    if (expedition.statut != 'publiee' or offer.statut != 'proposee'
            or expedition.offres.filter(statut='acceptee').exists()):
        messages.error(request, 'Cette offre ne peut plus être acceptée.')
    elif not offer.vehicule.disponible:
        messages.error(request, 'Le véhicule de cette offre n’est plus disponible.')
    else:
        offer.expedition = expedition
        offer.statut = 'acceptee'
        try:
            offer.save(update_fields=['statut', 'updated_at'])
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
        else:
            messages.success(request, 'Offre acceptée. L’expédition est maintenant attribuée.')
    return redirect('offre_detail', pk=pk)
