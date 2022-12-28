from django.urls import path
from . import views

urlpatterns = [
    path('',  views.getRoutes),
    path('investors', views.getInvestors),
    path('investor/<str:em>', views.getInvestor),
    path('create-investor', views.createInvestor),
    path('update-investor', views.updateInvestor),
    path('search-investors', views.searchInvestors),
    path('delete-investor/<str:em>', views.deleteInvestor),
    path('generate-auth', views.getAuthToken),
]