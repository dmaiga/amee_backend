from django.urls import path
from roster.views import (
    SoumettreCandidatureView,
    ValiderCandidatureView,
    MonProfilRosterView,
    ListeConsultantsPublicView,
    DetailConsultantPublicView
)

urlpatterns = [
    # --- INTERNE ---
    path('me/', MonProfilRosterView.as_view()),
    path('soumettre/', SoumettreCandidatureView.as_view()),
    path('<int:pk>/valider/', ValiderCandidatureView.as_view()),

    # --- PUBLIC ---
    path('public/', ListeConsultantsPublicView.as_view()),
    path('public/<int:pk>/', DetailConsultantPublicView.as_view()),
]
