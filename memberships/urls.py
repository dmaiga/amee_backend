from django.urls import path
from memberships.views import (
    MonAdhesionView,
    
    
)

urlpatterns = [
    path('me/', MonAdhesionView.as_view()),
    
 ]
