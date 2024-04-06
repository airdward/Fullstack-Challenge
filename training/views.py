from django.contrib.auth.models import User
from django.db.models import Prefetch, Count, F, Q, Sum
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from training.models import Activity, UserActivity, UserActivityLog, do_training

from training.serializers import UserActivityLogSerializer

#Going with the assumption that our hardcoded user_id is 1
class ActivityBegunView(APIView):
    def post(self, request):

        activity_id = request.data.get("activity_id")
        user_id = 1  

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user_activity = UserActivity.objects.create(user_id=user_id, activity=activity)
        user_activity_log = UserActivityLog.objects.create(
            user_activity=user_activity, score=0
        )

        return Response(
            {"message": f"{activity.name} Activity has begun already"},
            status=status.HTTP_201_CREATED,
        )


class ActivityDoneView(APIView):
    def post(self, request):
        activity_id = request.data.get("activity_id")
        user_id = 1 

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response(
                {"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user_activity = UserActivity.objects.get(user_id=user_id, activity=activity)
        if user_activity.completed:
            return Response({"error": "Already Done"}, status=status.HTTP_200_OK)

        # Mark activity as done
        user_activity.completed = True
        user_activity_log = UserActivityLog.objects.get(user_activity=user_activity)
        user_activity_log.score = do_training()

        user_activity.save()

        return Response(
            {"message": f"{activity.name} Training completed successfully"},
            status=status.HTTP_200_OK,
        )
class ProgressView(APIView):
    def get(self, request):
        # Assuming user ID 1 for testing
        user_id = 1

        user_activity_logs = UserActivityLog.objects.filter(user_activity__user_id=user_id
        ).prefetch_related(Prefetch("user_activity__activity__name", to_attr="prefetched_activity")
        ).values(
            "score",
            "started_at",
            "ended_at",
            activity_name=F("prefetched_activity__name"),  # Reuse prefetched data
            completed=F("user_activity__completed"),
        )

        serializer = UserActivityLogSerializer(user_activity_logs, many=True)

        total_score = UserActivity.objects.filter(
            completed=True, user_id=user_id
        ).aggregate(total_score=Sum("useractivitylog__score"))

        user_profile = {
            "username": User.objects.get(id=user_id).username,  # Access username
            "total_score": total_score["total_score"],
        }

        return Response(
            {"user_profile": user_profile, "user_progress": serializer.data},
            status=status.HTTP_200_OK,
        )
class LeaderboardView(APIView):
    def get(self, request):
        leaderboard_data = (
            UserActivity.objects.filter(completed=True)
            .select_related("user")  # Prefetch related user data
            .values(
                "user__username",
                total=Sum("useractivitylog__score"),
                completed_count=Count("id", filter=Q(completed=True)),
            )
            .order_by("-total")
        )

        return Response({"leaderboard": leaderboard_data}, status=status.HTTP_200_OK)
