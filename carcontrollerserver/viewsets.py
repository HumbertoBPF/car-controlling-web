from django.shortcuts import get_object_or_404
from carcontrollerserver.permissions import IsAuthenticatedPost
from rest_framework.response import Response
from carcontrollerserver.models import Game, Score
from carcontrollerserver.serializers import GameSerializer, ScoreCreatorSerializer, ScoreSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication

class GameViewSet(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class ScoreViewSet(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedPost]

    def get(self, request):
        scores = Score.objects.all()
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        serializer = ScoreCreatorSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid(raise_exception=True):
            score = serializer.save()
            serializer = ScoreSerializer(score)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
