import pytest

from random import randint
from urllib.parse import urlencode
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from carcontrollerserver.models import AppUser, Game
from carcontrollerserver.tests.conftest import get_random_string
from carcontrollerserver.validators import is_valid_user_data


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

    assert len(response.context.get('ads')) == len(ads)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        '',
        'test@test.com',
        get_random_string(randint(1, 8)) + ' ' + get_random_string(randint(1, 8)) + '@test.com'
    ]
)
@pytest.mark.parametrize(
    'username', [
        'test',
        '',
        get_random_string(randint(1, 6)) + ' ' + get_random_string(randint(1, 6))
    ]
)
@pytest.mark.parametrize(
    'password', [
        'password',
        '',
        get_random_string(8) + ' ' + get_random_string(1),
        get_random_string(randint(1, 5)),
        get_random_string(randint(31, 40))
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
    assert is_valid_user_data(email, username, password, password_confirmation)[0] == \
           ((email == 'test@test.com') and (username == 'test') and (password == 'password') and (password_confirmation == 'password'))


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
        print("Testing validation of field uniqueness for user " + str(i) + " of " + str(k))
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
        '',
        'test@test.com',
        get_random_string(randint(1, 8)) + ' ' + get_random_string(randint(1, 8)) + '@test.com'
    ]
)
@pytest.mark.parametrize(
    'username', [
        'test',
        '',
        get_random_string(randint(1, 6)) + ' ' + get_random_string(randint(1, 6))
    ]
)
@pytest.mark.parametrize(
    'password', [
        'password',
        '',
        get_random_string(8) + ' ' + get_random_string(1),
        get_random_string(randint(1, 5)),
        get_random_string(randint(31, 40))
    ]
)
@pytest.mark.parametrize(
    'password_confirmation', [
        'password',
        get_random_string(randint(6, 30))
    ]
)
def test_signup_validation_error(client, email, username, password, password_confirmation):
    """Test the validation errors that may happen in the signup endpoint"""
    data = {"email": email,
            "username": username,
            "password": password,
            "password_confirmation": password_confirmation
            }
    url = reverse('signup')

    response = client.post(url, data)

    is_successful_test_case = \
        (email == 'test@test.com') and (username == 'test') and (password == 'password') and (password_confirmation == 'password')
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/signup-form"
    assert User.objects.filter(email=email, username=username).exists() == is_successful_test_case
    assert AppUser.objects.filter(user__email=email, user__username=username).exists() == is_successful_test_case


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_repeated_username', [True, False]
)
@pytest.mark.parametrize(
    'is_repeated_email', [True, False]
)
def test_signup_repeated_credentials(client, create_users, is_repeated_username, is_repeated_email):
    """Test the signup with username and/or email of an existing user"""
    nb_users = randint(5, 10)
    users = create_users(k=nb_users)

    url = reverse('signup')
    data = {
        "email": users[randint(0, len(users) - 1)].email if is_repeated_email else get_random_string(randint(6, 18)) + "@test.com",
        "username": users[randint(0, len(users) - 1)].username if is_repeated_username else get_random_string(randint(6, 18)),
        "password": "strong-password",
        "password_confirmation": "strong-password"
    }

    response = client.post(url, data)

    is_successful = (not is_repeated_email) and (not is_repeated_username)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/signup-form"
    assert User.objects.count() == nb_users + 1 if is_successful else nb_users
    assert AppUser.objects.count() == nb_users + 1 if is_successful else nb_users


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        None,
        get_random_string(randint(10, 16)) + "@test.com"
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
    """Test the access to the signup endpoint with some required fields missing"""
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
    is_successful =  \
        (email is not None) and (username is not None) and (password is not None) and (password_confirmation is not None)
    assert response.url == "/account/signup-form" if is_successful else "/dashboard"
    # Verifying if the User and the AppUser records were created
    assert User.objects.filter(email=email, username=username).exists() is is_successful
    assert AppUser.objects.filter(user__email=email, user__username=username).exists() is is_successful


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
        None
    ]
)
def test_profile_valid_game_filter(client, scores, game):
    """Testing the access to the profile page with some fields on the game history (filters the games to be shown)"""
    print()
    user = User.objects.first()
    client.login(username=user.username, password='strong-password')

    url = reverse('profile')
    if game is not None:
        query = urlencode({'game': game})
        url = '{}?{}'.format(url, query)

    response = client.get(url)

    selected_game = response.context.get('selected_game')

    scores_matched = response.context.get('scores')
    print("Number of scores returned: " + str(len(scores_matched)))

    # Verifying the value of 'selected_game' context variable (should be the game corresponding to the GET parameter 'game')
    assert selected_game.game_tag == game if game is not None else Game.objects.first().game_tag

    for score in scores_matched:
        # All scores should refer to the selected game
        assert score.game == selected_game

    for score in scores_matched:
        # All scores should belong to the authenticated user
        assert score.user == user
    # Check if all the games existing in the database were returned to the 'games' response parameter
    games = response.context.get('games')
    assert len(games) == Game.objects.count()
    # Checking if the returned app_user is associated with the authenticated user
    app_user = response.context.get('app_user')
    assert app_user.user == user
    # Checking if the form object is present in the response
    form_picture = response.context.get('form_picture')
    assert form_picture is not None

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_profile_invalid_game_filter(client, scores):
    """Tests the access to the profile page with an invalid game filter"""
    print()
    user = User.objects.first()
    client.login(username=user.username, password='strong-password')
    base_url = reverse('profile')
    query = urlencode({'game': get_random_string(12)})
    url = '{}?{}'.format(base_url, query)

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'filename, status_code, has_picture', [
        ('C:/Users/Humberto/Desktop/Humberto/Study/WebDev/car-controller-app/requirements.txt', status.HTTP_200_OK,
         False),
        (None, status.HTTP_302_FOUND, False),
        ('C:/Users/Humberto/Desktop/Humberto/Study/WebDev/car-controller-app/application/static/logo.png',
         status.HTTP_302_FOUND, True)
    ]
)
def test_change_picture(client, create_users, filename, status_code, has_picture):
    """Tests the endpoint to change the profile picture with different file formats"""
    user = create_users()[0]
    client.login(username=user.username, password='strong-password')
    url = reverse('change-picture')

    if filename is not None:
        with open(filename, 'rb') as fp:
            response = client.post(url, {'picture': fp})
    else:
        response = client.post(url)

    app_user = AppUser.objects.filter(user__username=user.username).first()
    assert response.status_code == status_code
    # Verify if there is a picture associated with the concerned profile when necessary
    assert app_user is not None
    assert bool(app_user.picture) == has_picture


@pytest.mark.django_db
@pytest.mark.parametrize(
    'game', [
        'driving_game',
        'obstacle_game',
        'parking_game',
        None
    ]
)
def test_rankings_ok_response(client, scores, game):
    """Tests the rankings endpoint with a valid game filter"""
    print()
    url = reverse('rankings')
    if game is not None:
        query = urlencode({'game': game})
        url = '{}?{}'.format(url, query)

    response = client.get(url)

    selected_game = response.context.get('selected_game')
    # When the game filter is not specified as a GET parameter, the scores associated with the first game of the db must be returned
    assert selected_game.game_tag == (game if game is not None else Game.objects.first().game_tag)
    # Check if all the games existing in the database were returned to the 'games' response parameter
    games = response.context.get('games')
    assert len(games) == Game.objects.count()

    scores_matched = response.context.get('scores')
    print("Number of scores returned: " + str(len(scores_matched)))
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


@pytest.mark.django_db
def test_delete_account(client, create_users):
    """Tests the endpoint for account deletion"""
    user = create_users()[0]
    client.login(username=user.username, password='strong-password')
    url = reverse('delete-account')
    response = client.post(url)

    assert not User.objects.filter(username=user.username, email=user.email).exists()
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/dashboard"


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        '',
        'test@test.com',
        get_random_string(randint(1, 8)) + ' ' + get_random_string(randint(1, 8)) + '@test.com'
    ]
)
@pytest.mark.parametrize(
    'username', [
        'test',
        '',
        get_random_string(randint(1, 6)) + ' ' + get_random_string(randint(1, 6))
    ]
)
@pytest.mark.parametrize(
    'password', [
        'password',
        '',
        get_random_string(8) + ' ' + get_random_string(1),
        get_random_string(randint(1, 5)),
        get_random_string(randint(31, 40))
    ]
)
@pytest.mark.parametrize(
    'password_confirmation', [
        'password',
        get_random_string(randint(6, 30))
    ]
)
def test_update_account_validation_error(client, create_users, email, username, password, password_confirmation):
    """Test the validation errors that may happen in the endpoint for account update"""
    user = create_users()[0]
    client.login(username=user.username, password='strong-password')
    data = {"email": email,
            "username": username,
            "password": password,
            "password_confirmation": password_confirmation
            }
    url = reverse('update-account')

    response = client.post(url, data)

    is_successful_test_case = \
        (email == 'test@test.com') and (username == 'test') and (password == 'password') and (password_confirmation == 'password')
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == ("/account/profile" if is_successful_test_case else "/account/update-form")
    assert User.objects.filter(id=user.id, email=email, username=username).exists() == is_successful_test_case
    assert AppUser.objects.filter(id=user.id, user__email=email, user__username=username).exists() == is_successful_test_case


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_other_user_username', [True, False]
)
@pytest.mark.parametrize(
    'is_other_user_email', [True, False]
)
def test_update_account_fail_due_to_repeated_credentials(client, create_users, is_other_user_username, is_other_user_email):
    """Tests the update account endpoint when the specified username and/or email are not available"""
    users = create_users(k=randint(5, 10))
    user = users[0]
    i = randint(1, len(users) - 1)
    client.login(username=user.username, password='strong-password')

    url = reverse('update-account')
    data = {
        "email": users[i].email if is_other_user_email else get_random_string(randint(6, 18)) + "@test.com",
        "username": users[i].username if is_other_user_username else get_random_string(randint(6, 18)),
        "password": "strong-password",
        "password_confirmation": "strong-password"
    }

    response = client.post(url, data)

    is_successful = (not is_other_user_username) and (not is_other_user_email)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/profile" if is_successful else "/account/update-form"
    assert User.objects.filter(id=user.id, email=data["email"], username=data["username"]).exists() is is_successful
    assert AppUser.objects.filter(id=user.id, user__email=data["email"], user__username=data["username"]).exists() is is_successful


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_same_username', [True, False]
)
@pytest.mark.parametrize(
    'is_same_email', [True, False]
)
def test_update_account_success_with_same_credentials(client, create_users, is_same_username, is_same_email):
    """Tests the update of an account when the username and/or email of the user remain the same"""
    users = create_users(k=randint(5, 10))
    user = users[0]
    client.login(username=user.username, password='strong-password')

    url = reverse('update-account')
    data = {
        "email": user.email if is_same_email else get_random_string(randint(6, 18)) + "@test.com",
        "username": user.username if is_same_username else get_random_string(randint(6, 18)),
        "password": "strong-password",
        "password_confirmation": "strong-password"
    }

    response = client.post(url, data)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/account/profile"
    assert User.objects.filter(id=user.id, email=data["email"], username=data["username"]).exists()
    assert AppUser.objects.filter(id=user.id, user__email=data["email"], user__username=data["username"]).exists()
