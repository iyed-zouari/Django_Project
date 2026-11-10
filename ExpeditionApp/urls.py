from django.urls import path
from .views import Liste_exprditions, home,welcome,detailleExpedition,deleteExpedition,listExpeditions,Detaille_expedition,Delete_expedition,Create_expedition,Update_expedition

urlpatterns = [
    path("home/", home, name="home"),
    path("welcome/<str:name>/", welcome, name="welcome"),
    path("list/", listExpeditions, name="list_expeditions"),
    path("detail/<str:reference>/", detailleExpedition, name="detail_expedition"),
    path("delete/<str:reference>/", deleteExpedition, name="delete_expedition"),
    path("listview/", Liste_exprditions.as_view(), name="listview_expeditions"),
    path("detailview/<int:pk>/", Detaille_expedition.as_view(), name="detailview_expedition"),
    path("deleteview/<int:pk>/", Delete_expedition.as_view(), name="deleteview_expedition"),
    path("createview/", Create_expedition.as_view(), name="createview_expedition"),
    path("updateview/<int:pk>/", Update_expedition.as_view(), name="updateview_expedition"),
    ]

