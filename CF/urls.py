from django.urls import path
from django.shortcuts import render
from . import views


urlpatterns = [
    path('',views.index, name='index'),
    path('centre-formation/', views.centre_formation_view, name='centre_formation'),
    path('centre-formation/<int:pk>/', views.centre_detail, name='centre_detail'),
    path('region/',views.region_view, name='region'),
    path('region/<int:pk>/', views.region_detail, name='region_detail'),

    path('prefecture/',views.prefecture_view, name='prefecture'),
    path('prefecture/<int:pk>/', views.prefecture_detail, name='prefecture_detail'),
    path('sousprefecture/',views.sousprefecture_view, name='sous_prefecture'),
    path('sousprefecture/<int:pk>/', views.sousprefecture_detail, name='sousprefecture_detail'),
    path('commune/',views.commune_view, name='commune'),
    path('commune/<int:pk>/', views.commune_detail, name='commune_detail'),
    path('secteur/',views.secteur_view, name='secteur'),
    path('publiccible/',views.publiccible_view, name='publiccible'),
]
