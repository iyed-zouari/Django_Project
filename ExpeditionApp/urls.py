from django.urls import path
from django.views.generic import RedirectView

from .views import (
    ExpeditionCreateView, ExpeditionDeleteView, ExpeditionDetailView,
    ExpeditionListView, ExpeditionUpdateView,
)


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='listview_expeditions'), name='expedition_home'),
    path('welcome/<str:name>/', RedirectView.as_view(url='/'), name='welcome'),
    path('list/', ExpeditionListView.as_view(), name='list_expeditions'),
    path('detail/<str:reference>/', ExpeditionDetailView.as_view(), name='detail_expedition'),
    path('delete/<str:reference>/', ExpeditionDeleteView.as_view(), name='delete_expedition'),
    path('listview/', ExpeditionListView.as_view(), name='listview_expeditions'),
    path('detailview/<int:pk>/', ExpeditionDetailView.as_view(), name='detailview_expedition'),
    path('deleteview/<int:pk>/', ExpeditionDeleteView.as_view(), name='deleteview_expedition'),
    path('createview/', ExpeditionCreateView.as_view(), name='createview_expedition'),
    path('updateview/<int:pk>/', ExpeditionUpdateView.as_view(), name='updateview_expedition'),
]
