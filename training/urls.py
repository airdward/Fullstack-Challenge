from django.urls import path

from training.views import (
    ProgressView,
    LeaderboardView,
    ActivityDoneView,
    ActivityBegunView,
)

urlpatterns = [
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("activity-done/", ActivityDoneView.as_view(), name="activity_done"),
    path("progress/", ProgressView.as_view(), name="progress"),
    path("activity-begun/", ActivityBegunView.as_view(), name="activity_begun"),
]
