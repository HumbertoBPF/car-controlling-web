import random
import pytest
import string

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from carcontrollerserver.models import Ads, AppUser, Game, Score
from django.contrib.auth.models import User
from rest_framework.test import APIClient


def get_random_string(size):
    allowed_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(allowed_chars) for x in range(size))


@pytest.fixture(scope="class", params=["Firefox", "Edge", "Chrome"])
def driver(request):
    if request.param == "Firefox":
        driver = webdriver.Firefox(service=Service("C:/Users/Humberto/Downloads/geckodriver.exe"))
    elif request.param == "Edge":
        driver = webdriver.Edge(service=Service("C:/Users/Humberto/Downloads/msedgedriver.exe"))
    else:
        driver = webdriver.Chrome(service=Service("C:/Users/Humberto/Downloads/chromedriver.exe"))
    yield driver
    driver.close()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def ads():
    ad1 = Ads(title="ad 1", description="This is the first ad")
    ad2 = Ads(title="ad 2", description="This is the second ad")
    ad3 = Ads(title="ad 3", description="This is the third ad")
    with open('C:/Users/Humberto/Desktop/Humberto/Study/WebDev/car-controller-app/application/static/logo.png', 'rb') as fp:    
        ad1.picture.save('myphoto.jpg', fp, save=False)
        ad2.picture.save('myphoto.jpg', fp, save=False)
        ad3.picture.save('myphoto.jpg', fp, save=False)
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
    users = create_users(k=k)
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
                username = get_random_string(random.randint(6, 12))
            # Email is a random uuid4 identifier if it is not specified
            if kwargs.get('email') is not None:
                email = kwargs.get('email')

                if i > 0:
                    email += (" " + i)
            else:
                email = get_random_string(random.randint(10, 16))+"@test.com"
            # Password is 'strong-password' if it is not specified
            if kwargs.get('password') is not None:
                password = kwargs.get('password')
            else:
                password = 'strong-password'

            user = User.objects.create_user(username=username, email=email, password=password)
            app_user = AppUser(user=user)
            app_user.save()
            users.append(user)

        return users
    return make_user
