from django.urls import path
from .views import CreateFeedbackView

urlpatterns = [
    path(
        "feedback/<int:pk>/",
        CreateFeedbackView.as_view(),
        name="create-feedback"
    ),
]
