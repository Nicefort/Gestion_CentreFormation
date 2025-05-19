from django.urls import path
from django.shortcuts import render
from . import views


urlpatterns = [
    path('',views.index, name='index'),
    path('centre-formation/', views.centre_formation_view, name='centre_formation'),
    #path('success/', lambda request: render(request, 'wizard/success.html'), name='success'),
    #path('calendrier ', views.calendar, name='calendrier' )
    path('region/',views.region_view, name='region'),
    path('region/<int:pk>/', views.region_view, name='region'),

    path('prefecture/',views.prefecture_view, name='prefecture'),
    path('sousprefecture/',views.sousprefecture_view, name='sous_prefecture'),
    path('commune/',views.commune_view, name='commune'),
    path('secteur/',views.secteur_view, name='secteur'),
    path('publiccible/',views.publiccible_view, name='publiccible'),
]
