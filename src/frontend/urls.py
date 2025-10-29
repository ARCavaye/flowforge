from .views import PlanDetailView
from django.urls import path

app_name = "frontend"

urlpatterns = [
    path("plans/<int:pk>/", PlanDetailView.as_view(), name="plan_detail"),
]
