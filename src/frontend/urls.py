from .views import PlanDetailView
from django.urls import path

urlpatterns = [
    path('plans/<int:pk>/', PlanDetailView.as_view(), name='plan_detail'),
]
