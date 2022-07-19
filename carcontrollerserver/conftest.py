import random
import uuid
import pytest
from carcontrollerserver.models import Ads, AppUser, Game, Score
from django.contrib.auth.models import User


@pytest.fixture
def ads():
    ad1 = Ads(title="ad 1", description="This is the first ad", picture=None)
    ad2 = Ads(title="ad 2", description="This is the second ad", picture=None)
    ad3 = Ads(title="ad 3", description="This is the third ad", picture=None)
    ad1.save()
    ad2.save()
    ad3.save()
    return Ads.objects.all()


@pytest.fixture
def games():
    driving_game = Game(game_tag='driving_game', game_name='Driving Game')
    obstacle_game = Game(game_tag='obstacle_game', game_name='Obstacle Game')
    parking_game = Game(game_tag='parking_game', game_name='Parking Game')
    driving_game.save()
    obstacle_game.save()
    parking_game.save()
    return Game.objects.all()


@pytest.fixture
def scores(create_users, games):
    k = random.randint(3, 5)
    create_users(k=k)
    users = User.objects.all()
    games = Game.objects.all()
    # Create from 3 to 5 scores for each user and for each game
    for user in users:
        for game in games:
            k = random.randint(3, 5)
            for _ in range(k):
                score = Score(user=user, game=game, score=random.randint(100,1000))
                score.save()
    
    return Score.objects.all()


@pytest.fixture
def create_users():
    def make_user(**kwargs):
        # k is the number of users that are going to be created (default value is 1)
        k = kwargs.get('k') if kwargs.get('k') is not None else 1

        users = []

        for i in range(k):
            print("Creating user "+str(i+1)+" of "+str(k))
            # Username is a random uuid4 identifier if it is not specified
            if kwargs.get('username') is not None:
                username = kwargs.get('username')
                
                if i > 0:
                    username += (" " + i)
            else:
                username = str(uuid.uuid4())
            # Email is a random uuid4 identifier if it is not specified
            if kwargs.get('email') is not None:
                email = kwargs.get('email')

                if i > 0:
                    email += (" " + i)
            else:
                email = str(uuid.uuid4())
            # Password is 'strong-password' if it is not specified
            if kwargs.get('password') is not None:
                password = kwargs.get('password')
            else:
                password = 'strong-password'

            user = User.objects.create_user(username=username, email=email, password=password)
            app_user = AppUser(user = user)
            app_user.save()
            users.append(user)

        return users
    return make_user