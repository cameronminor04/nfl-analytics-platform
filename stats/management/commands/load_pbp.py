import nflreadpy as nfl
import pandas as pd
from django.core.management.base import BaseCommand

from stats.models import Game, Play, Team

PLAY_COLS = [
    "game_id", "play_id", "posteam", "defteam", "qtr", "down", "ydstogo",
    "yardline_100", "play_type", "yards_gained", "epa", "success", "wp",
    "run_location", "run_gap", "pass_length", "pass_location",
    "passer_player_name", "rusher_player_name", "desc",
]


def clean(v):
    return None if pd.isna(v) else v


def to_int(v):
    v = clean(v)
    return None if v is None else int(v)


def to_float(v):
    v = clean(v)
    return None if v is None else float(v)


def to_bool(v):
    v = clean(v)
    return None if v is None else bool(v)


def to_str(v):
    v = clean(v)
    return "" if v is None else str(v)


class Command(BaseCommand):
    help = "Load nflverse play-by-play data into Postgres (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument("seasons", nargs="+", type=int)

    def handle(self, *args, **opts):
        seasons = opts["seasons"]
        self.stdout.write(f"Downloading seasons {seasons}...")
        df = nfl.load_pbp(seasons).to_pandas()
        df = df[df["game_id"].notna() & df["play_id"].notna()]

        # Teams
        abbrs = set(df["home_team"].dropna()) | set(df["away_team"].dropna())
        Team.objects.bulk_create([Team(abbr=a) for a in abbrs], ignore_conflicts=True)

        # Games (one row per game_id)
        games = df.drop_duplicates("game_id")
        Game.objects.bulk_create(
            [
                Game(
                    game_id=r["game_id"],
                    season=int(r["season"]),
                    week=int(r["week"]),
                    season_type=to_str(r["season_type"]),
                    game_date=clean(r["game_date"]),
                    home_team_id=r["home_team"],
                    away_team_id=r["away_team"],
                    home_score=to_int(r["home_score"]),
                    away_score=to_int(r["away_score"]),
                )
                for r in games.to_dict("records")
            ],
            ignore_conflicts=True,
        )

        # Plays
        rows = df[PLAY_COLS].to_dict("records")
        plays = [
            Play(
                game_id=r["game_id"],
                play_id=int(r["play_id"]),
                offense_id=clean(r["posteam"]),
                defense_id=clean(r["defteam"]),
                quarter=to_int(r["qtr"]),
                down=to_int(r["down"]),
                yards_to_go=to_int(r["ydstogo"]),
                yardline_100=to_int(r["yardline_100"]),
                play_type=to_str(r["play_type"]),
                yards_gained=to_int(r["yards_gained"]),
                epa=to_float(r["epa"]),
                success=to_bool(r["success"]),
                win_prob=to_float(r["wp"]),
                run_location=to_str(r["run_location"]),
                run_gap=to_str(r["run_gap"]),
                pass_length=to_str(r["pass_length"]),
                pass_location=to_str(r["pass_location"]),
                passer=to_str(r["passer_player_name"]),
                rusher=to_str(r["rusher_player_name"]),
                description=to_str(r["desc"]),
            )
            for r in rows
        ]
        Play.objects.bulk_create(plays, batch_size=5000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Teams: {Team.objects.count()}, "
            f"Games: {Game.objects.count()}, Plays: {Play.objects.count()}"
        ))