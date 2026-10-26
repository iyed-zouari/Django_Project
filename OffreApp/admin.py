from django.contrib import admin
from .models import Offre
from django.http import HttpResponse
from django.utils.html import format_html
import csv

@admin.action(description="Exporter la sélection en CSV")
def exporter_offres_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="offres.csv"'
    writer = csv.writer(response)
    writer.writerow(['reference_expedition', 'transporteur', 'prix', 'statut'])
    for offre in queryset.select_related('expedition', 'transporteur'):
        writer.writerow([
            offre.expedition.reference,
            offre.transporteur.raison_sociale,
            offre.prix,
            offre.statut
        ])
    return response

class FilterBYPrice(admin.SimpleListFilter):
    title = "Tranche de prix"
    parameter_name = "prix_range"

    def lookups(self, request, model_admin):
        return [
            ('low', '< 1000 DT'),
            ('medium', '1000 - 10000 DT'),
            ('high', '> 10000 DT')
        ]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(prix__lt=1000)
        if self.value() == 'medium':
            return queryset.filter(prix__gte=1000, prix__lte=10000)
        if self.value() == 'high':
            return queryset.filter(prix__gt=10000)
        return queryset
    
@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    list_filter = ('statut',)
    search_fields = ('expedition__reference', 'transporteur__raison_sociale')
    readonly_fields = ('date_proposition', 'created_at', 'updated_at')
    actions = [exporter_offres_csv]

    fieldsets = (
        ("Détails de l'offre", {'fields': ('expedition', 'transporteur', 'vehicule')}),
        ('Conditions financières', {'fields': ('prix', 'delai_jours', 'statut')}),
        ('Horodatage', {'fields': ('date_proposition', 'created_at', 'updated_at')}),
    )

    
    def get_readonly_fields(self, request, obj=None):
        base = list(self.readonly_fields)
        if obj and obj.statut == 'acceptee':
            return base + ['prix', 'delai_jours']
        return base



        
    @admin.display(description='Statut')
    def statut_colore(self, obj):
        couleurs = {
            'proposee': '#F0AD4E',  
            'acceptee': '#5CB85C',  
            'refusee': '#D9534F',   
            'retiree': '#777777',   
        }
        
        return format_html(
            '<span style="color:white; background:{}; padding:4px 8px; border-radius:4px; font-weight:bold;">{}</span>',
            couleurs.get(obj.statut, '#999'),
            obj.statut
        )