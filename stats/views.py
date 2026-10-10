from django.db.models import Avg, Count, IntegerField
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@api_view(["GET"])
def team_stats(request):
    side = request.query_params.get("side", "offense")
    field = "defense" if side == "defense" else "offense"

    qs = Play.objects.filter(
        play_type__in=["run", "pass"],
        epa__isnull=False,
        game__season_type="REG",
    )
    team = request.query_params.get("team")
    season = request.query_params.get("season")
    if team:
        qs = qs.filter(**{f"{field}_id": team.upper()})
    if season:
        qs = qs.filter(game__season=int(season))

    rows = (
        qs.values(field, "game__season")
        .annotate(
            plays=Count("id"),
            epa=Avg("epa"),
            success=Avg(Cast("success", IntegerField())),
        )
        .order_by("game__season", "-epa")
    )
    return Response([
        {
            "team": r[field],
            "season": r["game__season"],
            "side": field,
            "plays": r["plays"],
            "epa_per_play": round(r["epa"], 3),
            "success_rate": round(r["success"], 3),
        }
        for r in rows
    ])