from django.shortcuts import render
from django.http import HttpResponse

from ExpeditionApp.models import Expedition
# Create your views here.
def home(request):
    return HttpResponse("'<strong>Bienvenue sur l'application d'expédition !</strong>'")



def welcome(request,name):
    return HttpResponse(f"'<strong>Bienvenue sur l'application d'expédition {name} !</strong>'")


def listExpeditions(request):
    liste=Expedition.objects.filter(statut='publiee').order_by('date_souhaitee')
    
    return render(request, 'expedition/list.html', {'liste': liste})



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