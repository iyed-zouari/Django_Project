from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from ExpeditionApp.forms import ExpeditionForm
from ExpeditionApp.models import Expedition
# Create your views here.
def home(request):
    return HttpResponse("'<strong>Bienvenue sur l'application d'expédition !</strong>'")



def welcome(request,name):
    return HttpResponse(f"'<strong>Bienvenue sur l'application d'expédition {name} !</strong>'")


def listExpeditions(request):
    list=Expedition.objects.filter(statut='publiee').order_by('date_souhaitee')
    
    return render(request, 'expedition/list.html', {'liste': list})



def detailleExpedition(request, reference):
    try:
        expedition = Expedition.objects.get(reference=reference)
    except Expedition.DoesNotExist:
        return HttpResponse("Expédition non trouvée.", status=404)
    
    return render(request, 'expedition/detail.html', {'expedition': expedition})


def deleteExpedition(request, reference):
    try:
        expedition = Expedition.objects.get(reference=reference)
        expedition.delete()
        return HttpResponse(f"Expédition {reference} supprimée avec succès.")
    except Expedition.DoesNotExist:
        return HttpResponse("Expédition non trouvée.", status=404)
    
class Liste_exprditions (ListView):
    model = Expedition
    template_name = 'expedition/list.html'
    context_object_name = 'liste'

class Detaille_expedition(DetailView):
    model = Expedition
    template_name = 'expedition/detail.html'
    context_object_name = 'expedition'
    
class Delete_expedition(DeleteView):
    model = Expedition
    template_name = 'expedition/delete.html'
    success_url = reverse_lazy('listview_expeditions') # Redirige vers la liste après la suppression

class Create_expedition(CreateView):
    model = Expedition
    template_name = 'expedition/forms.html'
    #fields = '__all__'
    form_class = ExpeditionForm
    success_url = reverse_lazy('listview_expeditions') # Redirige vers la liste après la création

class Update_expedition(UpdateView):
    model = Expedition
    template_name = 'expedition/forms.html'
    form_class = ExpeditionForm
    success_url = reverse_lazy('listview_expeditions') # Redirige vers la liste après la mise à joura
    