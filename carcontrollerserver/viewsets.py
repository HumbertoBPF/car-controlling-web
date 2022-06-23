from functools import partial
from carcontrollerserver.permissions import IsAuthenticatedPost, IsNotAuthenticatedPost
from rest_framework.response import Response
from carcontrollerserver.models import Game, Score
from carcontrollerserver.serializers import GameSerializer, ScoreSerializer, UserSerializer
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
        serializer = ScoreSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserViewSet(APIView):
    authentication_class = [BasicAuthentication]
    permission_classes = [IsNotAuthenticatedPost]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"username": serializer.data.get('username'),"email": serializer.data.get('email')})
    
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({
            "username": serializer.data.get('username'),
            "email": serializer.data.get('email')
            }, status=status.HTTP_201_CREATED)

    def put(self, request):
        serializer = UserSerializer(instance=request.user, data=request.data, partial=True, context={"user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"username": serializer.data.get('username'),"email": serializer.data.get('email')})
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
