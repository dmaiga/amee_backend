from django.urls import path
from . import views

urlpatterns = [
    path('', views.acceuil, name='acceuil'),
    path('galeries/', views.gallery_list, name='public_gallery_list'),
    path('galeries/<slug:slug>/', views.gallery_detail, name='public_gallery_detail'),
    path('association/presentation/', views.about_association, name='about_association'),
    path('association/bureau/', views.board_list, name='board_list'),
    path('association/bureau/membre/<int:pk>/', views.board_member_detail, name='board_member_detail'),
    path('bureau/<int:pk>', views.organization_detail, name='organization_detail'),

    path('publications/', views.publications, name='publications'),
    path('publications/articles/<slug:slug>/', views.article_detail, name='pub_article_detail'),
    path('publications/opportunite/<int:pk>/', views.opportunity_detail, name='pub_opportunity_detail'),
    
    path('adhesion-info/', views.adhesion_info_view, name='adhesion_info'),
    path('contact/', views.contact_view, name='contact'),
]