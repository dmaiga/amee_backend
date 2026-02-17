from django.urls import path
from quality_control.views import CreateFeedbackView

urlpatterns = [
    path(
        "feedback/<int:pk>/",
        CreateFeedbackView.as_view(),
        name="create-feedback"
    ),
]
