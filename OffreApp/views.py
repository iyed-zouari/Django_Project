from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import OffreForm
from .models import Offre


class OffreListView(ListView):
    queryset = Offre.objects.select_related("expedition", "transporteur", "vehicule").order_by("-created_at")
    template_name = "offre/list.html"
    context_object_name = "offres"


class OffreDetailView(DetailView):
    model = Offre
    template_name = "offre/detail.html"
    context_object_name = "offre"


class OffreCreateView(CreateView):
    model = Offre
    form_class = OffreForm
    template_name = "offre/form.html"
    success_url = reverse_lazy("offre_list")


class OffreUpdateView(UpdateView):
    model = Offre
    form_class = OffreForm
    template_name = "offre/form.html"
    success_url = reverse_lazy("offre_list")


class OffreDeleteView(DeleteView):
    model = Offre
    template_name = "offre/delete.html"
    context_object_name = "offre"
    success_url = reverse_lazy("offre_list")
