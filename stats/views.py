from rest_framework import viewsets
from .models import Game, Play, Team
from .serializers import GameSerializer, PlaySerializer, TeamSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.order_by("abbr")
    serializer_class = TeamSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.order_by("season", "week")
    serializer_class = GameSerializer


class PlayViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlaySerializer

    FILTERS = {
        "offense": "offense_id",
        "defense": "defense_id",
        "season": "game__season",
        "week": "game__week",
        "down": "down",
        "play_type": "play_type",
    }

    def get_queryset(self):
        qs = Play.objects.order_by("game_id", "play_id")
        for param, field in self.FILTERS.items():
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        return qs
