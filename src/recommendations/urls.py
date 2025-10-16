from django.urls import path

from . import views

app_name = "recommendations"

urlpatterns = [
    # Recommendations Tracking URLs
    path("", views.recommendations_home, name="recommendations_home"),
    path("new/", views.recommendations_new, name="recommendations_new"),
    path("manage/", views.recommendations_manage, name="recommendations_manage"),
    path("area/<str:area_slug>/", views.recommendations_by_area, name="recommendations_by_area"),
]