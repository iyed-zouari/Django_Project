from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from EntrepriseApp.profile_views import delete_account, profile
from EntrepriseApp.views import register
from .views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('connexion/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('deconnexion/', LogoutView.as_view(), name='logout'),
    path('inscription/', register, name='register'),
    path('profil/', profile, name='profile'),
    path('profil/supprimer/', delete_account, name='delete_account'),
    path('expedition/', include('ExpeditionApp.urls')),
    path('vehicules/', include('VehiculeApp.urls')),
    path('entreprises/', include('EntrepriseApp.urls')),
    path('offres/', include('OffreApp.urls')),
]
