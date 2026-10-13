from django.contrib import admin
from .models import Offre


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    list_filter = ('statut',)
    search_fields = ('expedition__reference', 'transporteur__raison_sociale')
    readonly_fields = ('date_proposition', 'created_at', 'updated_at')
