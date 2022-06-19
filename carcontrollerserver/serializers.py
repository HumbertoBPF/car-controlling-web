from dataclasses import field
from carcontrollerserver.models import Game, Score
from rest_framework import serializers

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model=Game
        fields='__all__'

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model=Score
        fields='__all__'

class ScoreCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Score
        exclude=['id','user']

    def create(self, validated_data):
        game = validated_data.get("game")
        score = validated_data.get("score")
        score = Score(user=self.context.get("user"), game=game, score=score)
        score.save()
        return score
