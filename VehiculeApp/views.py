from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import VehiculeForm
from .models import Vehicule


class VehiculeListView(ListView):
    model = Vehicule
    template_name = "vehicule/list.html"
    context_object_name = "vehicules"
    queryset = Vehicule.objects.select_related("entreprise").order_by("immatriculation")


class VehiculeDetailView(DetailView):
    model = Vehicule
    template_name = "vehicule/detail.html"
    context_object_name = "vehicule"


class VehiculeCreateView(CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = "vehicule/form.html"
    success_url = reverse_lazy("vehicule_list")


class VehiculeUpdateView(UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = "vehicule/form.html"
    success_url = reverse_lazy("vehicule_list")


class VehiculeDeleteView(DeleteView):
    model = Vehicule
    template_name = "vehicule/delete.html"
    context_object_name = "vehicule"
    success_url = reverse_lazy("vehicule_list")
