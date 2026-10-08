from rest_framework.routers import DefaultRouter
from .views import GameViewSet, PlayViewSet, TeamViewSet

router = DefaultRouter()
router.register("teams", TeamViewSet)
router.register("games", GameViewSet)
router.register("plays", PlayViewSet, basename="play")

urlpatterns = router.urls