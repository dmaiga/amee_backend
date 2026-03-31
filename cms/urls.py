from django.urls import path
from .views import *

urlpatterns = [
    path("articles/", ArticleListView.as_view()),
    path("articles/<slug:slug>/", ArticleDetailView.as_view()),

    path("resources/", PublicResourceListView.as_view()),
    path("resources/<int:pk>/", PublicResourceDetailView.as_view()),

    path("opportunities/", PublicOpportunityListView.as_view()),
    path("opportunities/<int:pk>/", PublicOpportunityDetailView.as_view()),

    path("api/galeries/", GalleryListAPIView.as_view()),
    path("api/galeries/<slug:slug>/", GalleryDetailAPIView.as_view()),
   

]
