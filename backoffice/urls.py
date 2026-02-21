from django.urls import path, include
from .web_views import (
    backoffice_login, dashboard, demander_feedback, feedback_detail, feedback_detail, membres_list, missions_list, 
    roster_detail, roster_list, tresorerie_paiement, 
    membre_detail, roster_decision,mission_detail,
    transactions_list,transaction_detail,
    tresorerie_depense,incidents_list,

)
from backoffice import web_views

urlpatterns = [
    # --- AUTHENTIFICATION & ACCÈS ---
    path("login/", backoffice_login, name="bo_login"),
    path("dashboard/", dashboard, name="bo_dashboard"),

    # --- TRÉSORERIE (Source de vérité financière) ---
    path("tresorerie/", include("backoffice.api.tresorerie.urls")),
    path("tresorerie/dashboard/",web_views.enrolement_dashboard,name="bo_enrolement_dashboard"),
    
    path("tresorerie/paiement-bureau/",web_views.paiement_bureau,name="bo_paiement_bureau"),
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

    # ---  ---

    path("cms/", web_views.cms_dashboard, name="bo_cms_dashboard"),

    path("cms/articles/", web_views.articles_list, name="bo_articles_list"),
    path("cms/articles/create/", web_views.article_form, name="bo_article_create"),
    path("cms/articles/<int:article_id>/", web_views.article_detail, name="bo_article_detail"),
    path("cms/articles/<int:article_id>/edit/", web_views.article_form, name="bo_article_edit"),

    # ---  ---

    path("cms/ressources/", web_views.ressources_list, name="bo_ressources_list"),
    path("cms/ressources/create/", web_views.ressource_form, name="bo_ressource_create"),
    path("cms/ressources/<int:ressource_id>/", web_views.ressource_detail, name="bo_ressource_detail"),
    path("cms/ressources/<int:ressource_id>/edit/", web_views.ressource_form, name="bo_ressource_edit"),

    # ---  ---

    path("cms/opportunities/", web_views.opportunities_list, name="bo_opportunities_list"),
    path("cms/opportunities/create/", web_views.opportunity_form, name="bo_opportunity_create"),
    path("cms/opportunities/<int:opportunity_id>/", web_views.opportunity_detail, name="bo_opportunity_detail"),
    path("cms/opportunities/<int:opportunity_id>/edit/", web_views.opportunity_form, name="bo_opportunity_edit"),

    # ---  ---
    
    path("organisations/", web_views.organisations_list, name="bo_organisations_list"),
    path("organisations/create/", web_views.organisation_form, name="bo_organisation_create"),
    path("organisations/<int:organisation_id>/", web_views.organisation_detail, name="bo_organisation_detail"),
    path("organisations/<int:organisation_id>/edit/", web_views.organisation_form, name="bo_organisation_edit"),

]