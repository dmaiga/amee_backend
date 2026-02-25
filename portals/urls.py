from django.urls import path, include
from portals.views import *

urlpatterns = [
    # ==========================================
    # 1. AUTHENTIFICATION COMMUNE
    # ==========================================
    path("login/", plateforme_login, name="login"),
    path("logout/", plateforme_logout, name="logout"),

    # ==========================================
    # 2. ESPACE CLIENT (Institutions/Recruteurs)
    # ==========================================
    path("client/register/", ClientRegistrationAPIView.as_view(), name="client-register"),
    path("client/dashboard/", client_dashboard, name="client-dashboard"),
    
    # Roster & Experts (Vue Client)
    path("client/experts/", ExpertListView.as_view(), name="client_experts"),    
    path("client/experts/<int:consultant_id>/", ClientExpertDetailView.as_view(), name="client_expert_detail"),
    
    # Gestion des Missions (Besoins)
    path("client/missions/", ClientMissionListView.as_view(), name="client_missions"),
    path("client/missions/create/", ClientMissionCreateView.as_view(), name="client_mission_create"),
    path("client/missions/detail/<int:pk>/", ClientMissionDetailView.as_view(), name="client_mission_detail"),
    path("client/missions/<int:mission_id>/add-document/", mission_add_document, name="mission_add_document"),

    # Interactions & Collaborations
    path("client/request-contact/", request_contact_client, name="request_contact_client"),    
    path("client/collaborations/", client_collaborations, name="client_collaborations"),
    path("client/relancer/<int:pk>/", relancer_consultant, name="relancer_consultant"),
    
    # Qualité (Feedback Client)
    path("client/feedbacks/", client_feedback_list, name="client_feedback_list"),
    path("client/feedback/<int:pk>/", client_feedback_detail, name="client_feedback_detail"),
    path("client/donner-feedback/<int:pk>/", donner_feedback, name="client_feedback"),

    # Paramètres
    path("client/profil/", client_profile_settings, name="client_profile_settings"),

    # ==========================================
    # 3. ESPACE MEMBRE & CONSULTANT (Adhérents)
    # ==========================================
    path("espace/", portal_dashboard, name="portal_dashboard"),
    
    
    path("espace/profile/", member_profile, name="member_profile"),
    path("espace/edit_profile/", edit_profile, name="edit_profile"),
    
    path("espace/roster/", roster_dashboard, name="roster_dashboard"),
    path("espace/roster/postuler/", roster_postuler, name="roster_postuler"),
    path("espace/roster/editer/", roster_edit_profile, name="roster_edit_profile"),
    path("espace/roster/reexamen/", roster_reexamen, name="roster_reexamen"),

    path("espace/membership/",membership_detail, name="membership_detail",),

    path("espace/resources/",resources_list, name="resources_list",),
    path("espace/events/",events_list,name="events_list",),
    path("espace/opportunites/",opportunities_list, name="opportunities_list",),
    path("espace/opportunites/<int:pk>/",opportunity_detail, name="opportunity_detail",),

    path("sollicitations/", sollicitations_list,name="sollicitations_list"),
    path(
        "sollicitations/<int:pk>/",sollicitation_detail,name="consultant_sollicitation_detail" ),

    path("missions/",consultant_missions,name="consultant_missions"),
    path("missions/<int:pk>/", mission_detail, name="consultant_mission_detail"),
]