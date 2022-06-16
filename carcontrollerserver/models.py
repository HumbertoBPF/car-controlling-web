from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Game(models.Model):
    game_tag = models.CharField(max_length=30, unique=True, null=True, blank=True)
    game_name = models.CharField(max_length=30, default="", null=True, blank=True)

    def __str__(self):
        return self.game_name

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField() 