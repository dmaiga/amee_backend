from django.urls import path
from memberships.views import (
    MonAdhesionView,
    DemandeAdhesionView,
    ValidationAdhesionView
)

urlpatterns = [
    path('me/', MonAdhesionView.as_view()),
    path('demande_adhesion/', DemandeAdhesionView.as_view()),
    path('<int:pk>/valider/', ValidationAdhesionView.as_view()),
]
