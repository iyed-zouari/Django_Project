from django.urls import path

from .views import OffreCreateView, OffreDeleteView, OffreDetailView, OffreListView, OffreUpdateView

urlpatterns = [
    path("", OffreListView.as_view(), name="offre_list"),
    path("ajouter/", OffreCreateView.as_view(), name="offre_create"),
    path("<int:pk>/", OffreDetailView.as_view(), name="offre_detail"),
    path("<int:pk>/modifier/", OffreUpdateView.as_view(), name="offre_update"),
    path("<int:pk>/supprimer/", OffreDeleteView.as_view(), name="offre_delete"),
]
