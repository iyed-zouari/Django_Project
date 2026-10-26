from django.contrib import admin
from .models import Expedition
from django.utils import timezone
from OffreApp.models import Offre

class EnRetardFilter(admin.SimpleListFilter):
    title = 'en retard'
    parameter_name = 'en_retard'

    def lookups(self, request, model_admin):
        return [('oui', 'Oui'), ('non', 'Non')]

    def queryset(self, request, queryset):
        aujourd_hui = timezone.now().date()
        if self.value() == 'oui':
            return queryset.filter(statut='publiee', date_souhaitee__lt=aujourd_hui)
        if self.value() == 'non':
            return queryset.exclude(statut='publiee', date_souhaitee__lt=aujourd_hui)
        return queryset

class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = 'expedition'
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False

@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'statut', 'entreprise')
    list_filter = ('statut','ville_depart', EnRetardFilter)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    inlines = [OffreInline]

    fieldsets = (
        ("Détails de l'expédition", {
            'fields': ('reference', 'entreprise', 'ville_depart', 'ville_arrivee', 'poids_kg', 'statut', 'date_souhaitee', 'description')
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )