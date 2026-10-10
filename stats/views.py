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


RUN_LOCATIONS = {
    "inside": ["middle"],
    "outside": ["left", "right"],
    "left": ["left"],
    "middle": ["middle"],
    "right": ["right"],
}


@api_view(["GET"])
def team_stats(request):
    params = request.query_params
    side = params.get("side", "offense")
    field = "defense" if side == "defense" else "offense"

    qs = Play.objects.filter(epa__isnull=False, game__season_type="REG")

    play_type = params.get("play_type")
    if play_type in ("run", "pass"):
        qs = qs.filter(play_type=play_type)
    else:
        qs = qs.filter(play_type__in=["run", "pass"])

    location = params.get("location")
    if location:
        if location not in RUN_LOCATIONS:
            return Response({"error": "location must be inside, outside, left, middle, or right"}, status=400)
        qs = qs.filter(play_type="run", run_location__in=RUN_LOCATIONS[location])

    try:
        if params.get("down"):
            qs = qs.filter(down=int(params["down"]))
        if params.get("season"):
            qs = qs.filter(game__season=int(params["season"]))
    except ValueError:
        return Response({"error": "down and season must be numbers"}, status=400)

    if params.get("team"):
        qs = qs.filter(**{f"{field}_id": params["team"].upper()})

    rows = (
        qs.values(field, "game__season")
        .annotate(
            plays=Count("id"),
            epa=Avg("epa"),
            success=Avg(Cast("success", IntegerField())),
            yards=Avg("yards_gained"),
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
            "avg_yards": round(r["yards"], 2) if r["yards"] is not None else None,
        }
        for r in rows
    ])