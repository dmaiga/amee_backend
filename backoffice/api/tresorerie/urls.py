from django.urls import path
from .views import EnregistrerPaiementAPIView

urlpatterns = [
    path(
        "enregistrer-paiement/",
        EnregistrerPaiementAPIView.as_view()
    ),
]
