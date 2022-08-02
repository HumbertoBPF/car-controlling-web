import pytest

from random import randint
from urllib.parse import urlencode
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from carcontrollerserver.models import AppUser, Game
from carcontrollerserver.tests.conftest import get_random_string
from carcontrollerserver.validators import is_valid_user_data


# Create your tests here.
@pytest.mark.django_db
def test_dashboard_no_ads(client):
    """Tests that no error happens when there is no ads to be shown in the dashboard"""
    url = reverse('dashboard')
    
    response = client.get(url)
    
    assert len(response.context.get('ads')) == 0
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_dashboard_with_ads(client, ads):
    """Tests dashboard access when there are some ads to be shown"""
    url = reverse('dashboard')
    
    response = client.get(url)
    
    assert len(response.context.get('ads')) > 0
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        '',
        'test@test.com',
        get_random_string(randint(1, 8))+' '+get_random_string(randint(1, 8))+'@test.com'
    ]
)
@pytest.mark.parametrize(
    'username', [
        'test',
        '', 
        get_random_string(randint(1,6))+' '+get_random_string(randint(1,6))
    ]
)
@pytest.mark.parametrize(
    'password', [
        'password',
        '',
        get_random_string(8)+' '+get_random_string(1),
        get_random_string(randint(1,5)),
        get_random_string(randint(31,40))
    ]
)
@pytest.mark.parametrize(
    'password_confirmation', [
        'password',
        get_random_string(randint(6, 30))
    ]
)
def test_user_data_validator(email, username, password, password_confirmation):
    """Tests the validation of the email, username and password by the user validation function"""
    if (email == 'test@test.com') and (username == 'test') and (password == 'password') and (password_confirmation == 'password'):
        assert is_valid_user_data(email, username, password, password_confirmation)[0]
    else:
        assert not is_valid_user_data(email, username, password, password_confirmation)[0]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email, username', [
        (get_random_string(randint(10, 16)), get_random_string(randint(6, 12)))
    ]
)
def test_user_data_validator_unique_fields(create_users, email, username):
    """Tests the validation of username and email uniqueness by the user validator function"""
    print()
    k = randint(5, 10)
    users = create_users(k=k)
    for i in range(k):
        print("Testing validation of field uniqueness for user "+str(i)+" of "+str(k))
        # Repeated email and username
        assert not is_valid_user_data(users[i].email, users[i].username, 'strong-password', 'strong-password')[0]
        # Repeated email
        assert not is_valid_user_data(email, users[i].username, 'strong-password', 'strong-password')[0]
        # Repeated username
        assert not is_valid_user_data(users[i].email, username, 'strong-password', 'strong-password')[0]
        # Repeated email and username with existing user parameter
        assert is_valid_user_data(users[i].email, users[i].username, 'strong-password', 'strong-password', existing_user=users[i])[0]
        # Repeated email and username with existing user parameter
        assert is_valid_user_data(users[i].email, username, 'strong-password', 'strong-password', existing_user=users[i])[0]
        # Repeated email and username with existing user parameter
        assert is_valid_user_data(email, users[i].username, 'strong-password', 'strong-password', existing_user=users[i])[0]
    # unique email and password
    assert is_valid_user_data(email, username, 'strong-password', 'strong-password')[0]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, password', [
        (get_random_string(randint(6, 12)), get_random_string(randint(6, 30))),
        (None, get_random_string(randint(6, 30))),
        (get_random_string(randint(6, 12)), None)
    ]
)
def test_login_wrong_username_and_password(client, create_users, username, password):
    """Tests the case where the login fails due to wrong credentials"""
    print()
    k = randint(5, 10)
    create_users(k=k)

    url = reverse('login')
    data = {}
    
    if username is not None:
        data["username"] = username
    
    if password is not None:
        data["password"] = password

    response = client.post(url, data)
    
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/login-form"


@pytest.mark.django_db
def test_login_successful(client, create_users):
    """Tests successful login of a user"""
    print()
    user = create_users()[0]
    
    url = reverse('login')
    data = {"username": user.username, "password": "strong-password"}

    response = client.post(url, data)
    
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/dashboard"


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        None, 
        get_random_string(randint(10, 16))+"@test.com"
    ]
)
@pytest.mark.parametrize(
    'username', [
        None, 
        get_random_string(randint(6, 12))
    ]
)
@pytest.mark.parametrize(
    'password', [
        None, 
        '123456'
    ]
)
@pytest.mark.parametrize(
    'password_confirmation', [
        None, 
        '123456'
    ]
)
def test_signup_argument_missing(client, email, username, password, password_confirmation):
    """Test the access to the signup endpoint with some of the required fields missing"""
    data = {}
    url = reverse('signup')

    if email is not None:
        data["email"] = email
    
    if username is not None:
        data["username"] = username
    
    if password is not None:
        data["password"] = password

    if password_confirmation is not None:
        data["password_confirmation"] = password_confirmation

    response = client.post(url, data)
    
    assert response.status_code == status.HTTP_302_FOUND
    if (email is not None) and (username is not None) and (password is not None) and (password_confirmation is not None):
        assert response.url == "/account/signup-form"
        # Verifying if the User and the AppUser records were created
        assert User.objects.filter(email=email,username=username).exists()
        assert AppUser.objects.filter(user__email=email,user__username=username).exists()
    else:
        assert response.url == "/dashboard"


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url', [
        '/account/profile',
        '/account/delete',
        '/account/update-form',
        '/account/update',
        '/account/change-picture'
    ]
)
def test_authenticated_endpoints_unauthenticated(client, url):
    """Testing the redirecting to the login form when the authenticated endpoints are accessed without previous authentication"""
    response = client.get(url)
    
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/login-form"
    
    response = client.post(url)
    
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/login-form"


@pytest.mark.django_db
@pytest.mark.parametrize(
    'game', [
        'driving_game',
        'obstacle_game',
        'parking_game',
        'all_games'
    ]
)
def test_game_filter_ok_reponse(client, scores, game):
    """Testing the access to the profile page with some fields on the game history (filters the games to be shown)"""
    print()
    user = User.objects.first()
    client.login(
       username=user.username, password='strong-password'
    )
    base_url = reverse('profile')
    query = urlencode({'game': game})
    url = '{}?{}'.format(base_url, query)
    
    response = client.get(url)
    
    selected_game = response.context.get('selected_game')
    
    scores_matched = response.context.get('scores')
    print("Number of scores returned: "+str(len(scores_matched)))
    
    if selected_game is not None:
        # Verifying the value of 'selected_game' context variable (should be the game corresponding to the GET parameter 'game')
        assert selected_game.game_tag == game
        
        for score in scores_matched:
            # All scores should refer to the selected game
            assert score.game == selected_game

    for score in scores_matched:
        # All scores should belong to the authenticated user
        assert score.user == user
    # Check if all the games existing in the database were returned in the 'games' response parameter
    games = response.context.get('games')
    assert len(games) == len(Game.objects.all())
    # Checking if the returned appuser is associated with the authenticated user
    appuser = response.context.get('app_user')
    assert appuser.user == user
    # Checking if the form object is present in the response
    form_picture = response.context.get('form_picture')
    assert form_picture is not None
    
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_game_filter_not_found_response(client, scores):
    """Tests the access to the profile page with an invalid game filter"""
    print()
    user = User.objects.first()
    client.login(
       username=user.username, password='strong-password'
    )
    base_url = reverse('profile')
    query = urlencode({'game': get_random_string(12)})
    url = '{}?{}'.format(base_url, query)
    
    response = client.get(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'filename, status_code, has_picture', [
        ('C:/Users/Humberto/Desktop/Humberto/Study/WebDev/car-controller-app/requirements.txt', status.HTTP_200_OK, False),
        (None, status.HTTP_302_FOUND, False),
        ('C:/Users/Humberto/Desktop/Humberto/Study/WebDev/car-controller-app/application/static/logo.png', status.HTTP_302_FOUND, True)
    ]
)
def test_change_picture(client, create_users, filename, status_code, has_picture):
    """Tests the endpoint to change the profile picture with different file formats"""
    user = create_users()[0]
    client.login(
       username=user.username, password='strong-password'
    )
    url = reverse('change-picture')

    if filename is not None:
        with open(filename, 'rb') as fp:    
            response = client.post(url, {'picture': fp})
            assert response.status_code == status_code
    else:
        response = client.post(url)
        assert response.status_code == status_code
    
    appuser = AppUser.objects.filter(user__username=user.username).first()
    # Verify if there is a picture associated with the concerned profile when necessary
    assert appuser is not None
    assert bool(appuser.picture) == has_picture


@pytest.mark.django_db
@pytest.mark.parametrize(
    'game', [
        'driving_game',
        'obstacle_game',
        'parking_game'
    ]
)
def test_rankings_ok_response(client, scores, game):
    """Tests the rankings endpoint with a valid game filter"""
    print()
    base_url = reverse('rankings')
    query = urlencode({'game': game})
    url = '{}?{}'.format(base_url, query)
    
    response = client.get(url)

    selected_game = response.context.get('selected_game')
    # Verifying the value of 'selected_game' context variable (should be the game corresponding to the GET parameter 'game')
    assert selected_game is not None
    assert selected_game.game_tag == game
    # Check if all the games existing in the database were returned in the 'games' response parameter
    games = response.context.get('games')
    assert len(games) == len(Game.objects.all())

    scores_matched = response.context.get('scores')
    print("Number of scores returned: "+str(len(scores_matched)))
    # Here, each score is a dictionary due to the way that the scores query was built in the endpoint view
    for score in scores_matched:
        # All scores should refer to the selected game
        assert score.get('game') == selected_game.id
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_rankings_not_found_response(client, scores):
    """Tests the rankings endpoint with an invalid game filter"""
    print()
    base_url = reverse('rankings')
    query = urlencode({'game': get_random_string(12)})
    url = '{}?{}'.format(base_url, query)
    
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND