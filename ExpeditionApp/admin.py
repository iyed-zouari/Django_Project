from django.contrib import admin
from .models import Expedition


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'statut', 'entreprise')
    list_filter = ('statut',)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee')
    readonly_fields = ('reference', 'created_at', 'updated_at')
