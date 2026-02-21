from django.urls import path
from .views import *

urlpatterns = [
    path("articles/", ArticleListView.as_view()),
    path("articles/<slug:slug>/", ArticleDetailView.as_view()),

    path("resources/", ResourceListView.as_view()),
    path("resources/<int:pk>/", ResourceDetailView.as_view()),

    path("opportunities/", OpportunityListView.as_view()),
    path("opportunities/<int:pk>/", OpportunityDetailView.as_view()),

    

]
