from django.urls import path
from clients.views import *
urlpatterns = [
    path("register/", ClientRegistrationAPIView.as_view(), name="client-register"),
    path("dashboard/", client_dashboard, name="client-dashboard"),
    #
    path("experts/", ExpertListView.as_view(), name="client_experts"),    
    path("experts/<int:consultant_id>/",ClientExpertDetailView.as_view(),name="client_expert_detail"),
    #
    path("client/missions/create/", ClientMissionCreateView.as_view(),name="client_mission_create"),
    path("client/missions/", ClientMissionListView.as_view(), name="client_missions"),
    path('client/missions/detail/<int:pk>/', ClientMissionDetailView.as_view(), name='client_mission_detail'),
    path("client/missions/<int:mission_id>/add-document/",mission_add_document,name="mission_add_document"),

    path("request-contact/client/", request_contact_client, name="request_contact_client"),    
    #
    path("client/collaborations/",client_collaborations,name="client_collaborations",),
    path("relancer/<int:pk>/",relancer_consultant,name="relancer_consultant"),
    #
    path("client/feedback/<int:pk>/",donner_feedback,name="client_feedback"),
    path("feedbacks/",client_feedback_list,name="client_feedback_list",),
    path("feedback/<int:pk>/",client_feedback_detail,name="client_feedback_detail" ),

path("profil/",client_profile_settings,name="client_profile_settings",),

]