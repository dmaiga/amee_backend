from django.urls import path, include
from .web_views import (
    backoffice_login, dashboard, demander_feedback, feedback_detail, feedback_detail, membres_list, missions_list, 
    roster_detail, roster_list, tresorerie_paiement, 
    membre_detail, roster_decision,mission_detail,
    transactions_list,transaction_detail,
    tresorerie_depense,incidents_list,

)

urlpatterns = [
    # --- AUTHENTIFICATION & ACCÈS ---
    path("login/", backoffice_login, name="bo_login"),
    path("dashboard/", dashboard, name="bo_dashboard"),

    # --- TRÉSORERIE (Source de vérité financière) ---
    path("tresorerie/", include("backoffice.api.tresorerie.urls")),
    path("tresorerie/paiement/", tresorerie_paiement, name="bo_enregistrer_paiement"),
    path("tresorerie/transactions/",transactions_list,name="bo_transactions"),
    path("tresorerie/transactions/<int:transaction_id>/", transaction_detail, name="bo_transaction_detail"),

    path("tresorerie/depense/",tresorerie_depense,name="bo_depense"),

    # --- ESPACE MEMBRES (Gestion administrative) ---
    path("membres/", membres_list, name="bo_membres"),
    path("membres/<int:user_id>/", membre_detail, name="bo_membre_detail"),

    # --- ESPACE ROSTER (Validation des experts) ---
    path("roster/", roster_list, name="bo_roster"),
    path("roster/<int:profil_id>/", roster_detail, name="bo_roster_detail"),
    path("roster/<int:profil_id>/decision/", roster_decision, name="bo_roster_decision"),

    # --- MISSIONS & COLLABORATIONS ---
    path("missions/", missions_list, name="bo_missions"),
    path("missions/<int:mission_id>/", mission_detail, name="bo_mission_detail"),
    path("contacts/<int:contact_id>/demander-feedback/",demander_feedback,name="bo_demander_feedback"),
    # ---  ---
    path("qualite/incidents/",incidents_list,name="bo_incidents"),
    path("qualite/feedback/<int:feedback_id>/",feedback_detail,name="bo_feedback_detail"),

]