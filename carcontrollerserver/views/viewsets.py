from carcontrollerserver.permissions import IsAuthenticatedPost, IsNotAuthenticatedPost
from rest_framework.response import Response
from carcontrollerserver.models import Ads, Game, Score
from carcontrollerserver.serializers import AdsSerializer, GameSerializer, ScoreSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication

class GameViewSet(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class ScoreViewSet(APIView):
    '''
    Viewset handling the requests to the /api/scores endpoint.
    
    GET: does not require authentication and returns all the scores.\n
    POST: requires Basic Authentication. It creates a new score for the authenticated account. The request body JSON needs to 
    have the following format:
        
        {
            "score": score value(int),
            "game": game id(int)
        }

    '''
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
    '''
    ViewSet responsible for all the methods of the /api/users endpoint.

    GET: requires Basic Authentication. It returns the username and the email of the authenticated user.\n
    POST: unique HTTP verb that does not require authentication since it is used to create a new account. The credentials of the
    account(email, username and password) are passed in the request body JSON.\n
    PUT: requires Basic Authentication. It modifies the authenticated user account with the specified credentials(email, username
    and password).\n
    DELETE: requires Basic Authentication to then delete the authenticated account.
    '''
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
        serializer = UserSerializer(instance=request.user, data=request.data, context={"user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"username": serializer.data.get('username'),"email": serializer.data.get('email')})
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

class AdsViewSet(generics.ListAPIView):
    queryset = Ads.objects.all()
    serializer_class = AdsSerializer