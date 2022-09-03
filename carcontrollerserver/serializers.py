from carcontrollerserver.models import Ads, AppUser, Game, Score
from carcontrollerserver.validators import is_valid_user_data
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Score
        fields = '__all__'

    def create(self, validated_data):
        game = validated_data.get("game")
        score = validated_data.get("score")
        score = Score(user=self.context.get("user"), game=game, score=score)
        score.save()
        return score


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)

    def create(self, validated_data):
        email = validated_data.get("email")
        username = validated_data.get("username")
        password = validated_data.get("password")
        password_confirmation = validated_data.get("password")
        is_valid_data, error_msg, error_field = is_valid_user_data(email, username, password, password_confirmation)
        if not is_valid_data:
            raise serializers.ValidationError({error_field: [error_msg]})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        app_user = AppUser(user=user)
        app_user.save()
        return user

    def update(self, instance, validated_data):
        email = validated_data.get("email")
        username = validated_data.get("username")
        password = validated_data.get("password")
        password_confirmation = validated_data.get("password")
        is_valid_data, error_msg, error_field = is_valid_user_data(email, username, password, password_confirmation, existing_user=self.context.get("user"))
        if not is_valid_data:
            raise serializers.ValidationError({error_field: [error_msg]})
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.password = make_password(validated_data.get("password", instance.password))
        instance.save()
        return instance


class AdsSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    class Meta:
        model = Ads
        fields = '__all__'

    def get_picture(self, obj):
        # Verifies if the ad has a picture associated with it, before trying to extract the url
        if obj.picture:
            return obj.picture.url
        return ''
        