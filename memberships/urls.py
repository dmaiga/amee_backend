# memberships/api/urls.py
from django.urls import path
from .views import MembershipRegistrationView

urlpatterns = [
    path("inscription/", MembershipRegistrationView.as_view()),
]