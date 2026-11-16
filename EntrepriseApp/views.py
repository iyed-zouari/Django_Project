from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EntrepriseForm
from .models import Entreprise


class EntrepriseListView(ListView):
    queryset = Entreprise.objects.select_related("gerant").order_by("raison_sociale")
    template_name = "entreprise/list.html"
    context_object_name = "entreprises"


class EntrepriseDetailView(DetailView):
    model = Entreprise
    template_name = "entreprise/detail.html"
    context_object_name = "entreprise"


class EntrepriseCreateView(CreateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = "entreprise/form.html"
    success_url = reverse_lazy("entreprise_list")


class EntrepriseUpdateView(UpdateView):
    model = Entreprise
    form_class = EntrepriseForm
    template_name = "entreprise/form.html"
    success_url = reverse_lazy("entreprise_list")


class EntrepriseDeleteView(DeleteView):
    model = Entreprise
    template_name = "entreprise/delete.html"
    context_object_name = "entreprise"
    success_url = reverse_lazy("entreprise_list")
