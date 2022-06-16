from django.contrib import admin

from carcontrollerserver.models import Game, Score

class GameDisplay(admin.ModelAdmin):
    list_display = ('id', 'game_name','game_tag')
    list_display_links = ('id', 'game_name','game_tag')
    search_fields = ('game_name',)
    list_per_page = 10

class ScoreDisplay(admin.ModelAdmin):
    list_display = ('id', 'user','game', 'score')
    list_display_links = ('id', 'user','game', 'score')
    list_per_page = 10

# Register your models here.
admin.site.register(Game, GameDisplay)
admin.site.register(Score, ScoreDisplay)