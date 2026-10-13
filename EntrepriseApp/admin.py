from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Entreprise


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations personnelles', {
            'fields': ('email',)
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Informations complémentaires', {
            'fields': ('user_id', 'telephone', 'role')
        }),
    )
    list_display = ('user_id', 'username', 'email', 'role', 'is_superuser', 'is_active')
    readonly_fields = ('user_id', 'created_at', 'updated_at')


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'gerant')
    search_fields = ('raison_sociale', 'matricule_fiscal')
    list_filter = ('type_entreprise',)
