from django.urls import path
from accounts.views import MeView, RegisterView

urlpatterns = [
    path('me/', MeView.as_view()),
]
