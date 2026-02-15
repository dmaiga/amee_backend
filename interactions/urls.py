from django.urls import path
from .views import (
    RequestContactView,
    ConsultantInteractionsView,
    ClientInteractionsView,
    SuiviMissionView,
    TerminerMissionView,
    UpdateContactStatusView
)

urlpatterns = [
    path('request-contact/', RequestContactView.as_view()),
    path('consultant/me/', ConsultantInteractionsView.as_view()),
    path('client/me/', ClientInteractionsView.as_view()),
    path(
        '<int:pk>/update-status/',
        UpdateContactStatusView.as_view()
    ),
    
    path(
        "<int:pk>/terminer-mission/",
        TerminerMissionView.as_view()
    ),
    path(
    "<int:pk>/suivi/",
        SuiviMissionView.as_view()
    ),

    
]
