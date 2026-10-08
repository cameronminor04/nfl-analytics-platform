from django.db import models

class Team(models.Model):
    abbr = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=64, blank=True)
    conference = models.CharField(max_length=3, blank=True)
    division = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return self.abbr


class Game(models.Model):
    game_id = models.CharField(max_length=20, primary_key=True)
    season = models.IntegerField()
    week = models.IntegerField()
    season_type = models.CharField(max_length=4)  # REGULAR or PLAYOFFS
    game_date = models.DateField(null=True)
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="home_games")
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="away_games")
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)

    class Meta:
        indexes = [models.Index(fields=["season", "week"])]

    def __str__(self):
        return self.game_id


class Play(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="plays")
    play_id = models.IntegerField()
    offense = models.ForeignKey(Team, null=True, on_delete=models.PROTECT, related_name="offensive_plays")
    defense = models.ForeignKey(Team, null=True, on_delete=models.PROTECT, related_name="defensive_plays")
    quarter = models.IntegerField(null=True)
    down = models.IntegerField(null=True)
    yards_to_go = models.IntegerField(null=True)
    yardline_100 = models.IntegerField(null=True)
    play_type = models.CharField(max_length=16, blank=True)
    yards_gained = models.IntegerField(null=True)
    epa = models.FloatField(null=True)
    success = models.BooleanField(null=True)
    win_prob = models.FloatField(null=True)
    run_location = models.CharField(max_length=8, blank=True)
    run_gap = models.CharField(max_length=8, blank=True)
    pass_length = models.CharField(max_length=8, blank=True)
    pass_location = models.CharField(max_length=8, blank=True)
    passer = models.CharField(max_length=64, blank=True)
    rusher = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["game", "play_id"], name="unique_play_per_game")
        ]
        indexes = [
            models.Index(fields=["offense", "game"]),
            models.Index(fields=["down", "play_type"]),
        ]