from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import GameViewSet, PlayViewSet, TeamViewSet, team_stats

router = DefaultRouter()
router.register("teams", TeamViewSet)
router.register("games", GameViewSet)
router.register("plays", PlayViewSet, basename="play")

urlpatterns = router.urls + [path("team-stats/", team_stats)]