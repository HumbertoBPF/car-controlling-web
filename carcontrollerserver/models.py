from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Game(models.Model):
    game_tag = models.CharField(max_length=30, unique=True, null=False, blank=False)
    game_name = models.CharField(max_length=30, unique=True, null=False, blank=False)

    def __str__(self):
        return self.game_name

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.IntegerField() 
    date = models.DateTimeField(default=timezone.now, blank=False, null=False)

class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True, null=True)

class Ads(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    picture = models.ImageField(upload_to='ads/')