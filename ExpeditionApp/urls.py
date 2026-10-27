from django.urls import path
from .views import home,welcome,listExpeditions,detailleExpedition,deleteExpedition

urlpatterns = [
    path("home/", home, name="home"),
    path("welcome/<str:name>/", welcome, name="welcome"),
    path("list/", listExpeditions, name="list_expeditions"),
    path("detail/<str:reference>/", detailleExpedition, name="detail_expedition"),
    path("delete/<str:reference>/", deleteExpedition, name="delete_expedition"),
]

