from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.access import BusinessRoleMixin
from .forms import EntrepriseForm, RegistrationForm
from .models import Entreprise


@require_http_methods(['GET', 'HEAD', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            user = form.save()
        except ValidationError as exc:
            form.add_error(None, exc.messages)
        else:
            login(request, user)
            return redirect('entreprise_create')
    return render(request, 'accounts/register.html', {'form': form})


class OwnedEntrepriseMixin(BusinessRoleMixin):
    def get_queryset(self):
        return Entreprise.objects.filter(pk=self.company.pk)


class EntrepriseListView(OwnedEntrepriseMixin, ListView):
    template_name = 'entreprise/list.html'
    context_object_name = 'entreprises'


class EntrepriseDetailView(OwnedEntrepriseMixin, DetailView):
    template_name = 'entreprise/detail.html'
    context_object_name = 'entreprise'


class EntrepriseCreateView(BusinessRoleMixin, CreateView):
    require_company = False
    model = Entreprise
    form_class = EntrepriseForm
    template_name = 'entreprise/form.html'
    success_url = reverse_lazy('entreprise_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'entreprise'):
            if request.method in ('GET', 'HEAD'):
                destination = 'entreprise_list' if request.user.role == request.user.entreprise.type_entreprise else 'home'
                return redirect(destination)
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.gerant = self.request.user
        form.instance.type_entreprise = self.request.user.role
        return super().form_valid(form)


class EntrepriseUpdateView(OwnedEntrepriseMixin, UpdateView):
    form_class = EntrepriseForm
    template_name = 'entreprise/form.html'
    success_url = reverse_lazy('entreprise_list')


class EntrepriseDeleteView(OwnedEntrepriseMixin, DeleteView):
    template_name = 'entreprise/delete.html'
    context_object_name = 'entreprise'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if self.object.expeditions.exists() or self.object.vehicules.exists() or self.object.offres.exists():
            messages.error(self.request, 'Supprimez les éléments liés avant de supprimer cette entreprise.')
            return self.form_invalid(form)
        return super().form_valid(form)
