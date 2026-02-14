from django.urls import path
from missions.views import (
    MissionCreateView,
    MesMissionsView,
    MissionDetailView
)

urlpatterns = [
    path('creer/', MissionCreateView.as_view()),
    path('me/', MesMissionsView.as_view()),
    path('<int:pk>/', MissionDetailView.as_view()),
]
