import random
import pytest
import base64

from rest_framework import status
from django.contrib.auth.models import User
from carcontrollerserver.models import AppUser, Score
from carcontrollerserver.tests.conftest import get_random_string


def get_basic_auth_header(username, password):
    credentials = base64.b64encode(f'{username}:{password}'.encode('utf-8'))
    return 'Basic {}'.format(credentials.decode('utf-8'))


@pytest.mark.django_db
def test_users_authentication_get(api_client):
    url = "http://localhost:8000/api/users"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_users_authentication_put(api_client):
    url = "http://localhost:8000/api/users"
    response = api_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_users_authentication_delete(api_client):
    url = "http://localhost:8000/api/users"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_users_get(api_client, create_users):
    user = create_users()[0]
    url = "http://localhost:8000/api/users"
    response = api_client.get(url, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.data.keys()
    assert "email" in response.data.keys()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        None,                                       # Verifies that the email is required
        '',                                         # Verifies that the email cannot be empty
        'test@test.com',
        get_random_string(random.randint(1, 8))+' '+get_random_string(random.randint(1, 8))+'@test.com',
                                                    # Verifies that the email cannot contain spaces
        True,                                       # Verifies that this field only accepts strings as value
        False,                                      # Verifies that this field only accepts strings as value
        get_random_string(random.randint(1, 30)),   # Verifies that this field verifies if the string is an email
        35.5,                                       # Verifies that this field only accepts strings as value
        30                                          # Verifies that this field only accepts strings as value
    ]
)
@pytest.mark.parametrize(
    'username', [
        None,                                       # Verifies that this field is required
        'test',
        '',                                         # Verifies that username cannot be empty
        get_random_string(random.randint(1,6))+' '+get_random_string(random.randint(1,6))
                                                    # Verifies that username cannot contain spaces
    ]
)
@pytest.mark.parametrize(
    'password', [
        None,                                       # Verifies that the password is required
        'password',
        '',                                         # Verifies that the password cannot be empty
        get_random_string(8)+' '+get_random_string(1),
                                                    # Verifies that the password cannot contain spaces
        get_random_string(random.randint(1,5)),     # Verifies that the password is not too short
        get_random_string(random.randint(31,40)),   # Verifies that the password is not too long
        True,                                       # Verifies that this field only accepts strings as value
        False,                                      # Verifies that this field only accepts strings as value
        35.5,                                       # Verifies that this field only accepts strings as value
        30                                          # Verifies that this field only accepts strings as value
    ]
)
def test_users_post_validators(api_client, email, username, password):
    url = "http://localhost:8000/api/users"
    data = {}

    if email is not None:
        data["email"] = email

    if username is not None:
        data["username"] = username

    if password is not None:
        data["password"] = password

    response = api_client.post(url, data=data)

    if (email == 'test@test.com') and (username == 'test') and (password == 'password'):
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=username, email=email).exists()
        assert AppUser.objects.filter(user__username=username, user__email=email).exists()
        assert "username" in response.data.keys()
        assert "email" in response.data.keys()
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_users_post_repeated_fields(api_client, create_users):
    url = "http://localhost:8000/api/users"

    k = random.randint(5, 10)
    users = create_users(k=k)
    i = random.randint(0,k-1)
    
    repeated_username = users[i].username
    repeated_email = users[i].email

    username = get_random_string(random.randint(6, 18))
    email = get_random_string(random.randint(6, 18))+'@test.com'
    password = get_random_string(random.randint(6, 30))
    # Repeated username
    data = {
        "username": repeated_username,
        "email": email,
        "password": password
    }

    response = api_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Repeated email
    data = {
        "username": username,
        "email": repeated_email,
        "password": password
    }

    response = api_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_users_post_success(api_client, create_users):
    url = "http://localhost:8000/api/users"

    k = random.randint(5, 10)
    create_users(k=k)

    username = get_random_string(random.randint(6, 18))
    email = get_random_string(random.randint(6, 18))+'@test.com'
    password = get_random_string(random.randint(6, 30))
    
    data = {
        "username": username,
        "email": email,
        "password": password
    }

    response = api_client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username=username, email=email).exists()
    assert AppUser.objects.filter(user__username=username, user__email=email).exists()
    assert "username" in response.data.keys()
    assert "email" in response.data.keys()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email', [
        None,                                       # Verifies that the email is required
        '',                                         # Verifies that the email cannot be empty
        'test@test.com',
        get_random_string(random.randint(1, 8))+' '+get_random_string(random.randint(1, 8))+'@test.com',
                                                    # Verifies that the email cannot contain spaces
        True,                                       # Verifies that this field only accepts strings as value
        False,                                      # Verifies that this field only accepts strings as value
        get_random_string(random.randint(1, 30)),   # Verifies that this field verifies if the string is an email
        35.5,                                       # Verifies that this field only accepts strings as value
        30                                          # Verifies that this field only accepts strings as value
    ]
)
@pytest.mark.parametrize(
    'username', [
        None,                                           # Verifies that field is required
        'test',
        '',                                             # Verifies that username cannot be empty
        get_random_string(random.randint(1,6))+' '+get_random_string(random.randint(1,6))
                                                        # Verifies that username cannot contain spaces
    ]
)
@pytest.mark.parametrize(
    'password', [
        None,                                           # Verifies that the password is required
        'password',
        '',                                             # Verifies that the password cannot be empty
        get_random_string(8)+' '+get_random_string(1),  # Verifies that the password cannot contain spaces
        get_random_string(random.randint(1,5)),         # Verifies that the password is not too short
        get_random_string(random.randint(31,40)),       # Verifies that the password is not too long
        True,                                           # Verifies that this field only accepts strings as value
        False,                                          # Verifies that this field only accepts strings as value
        35.5,                                           # Verifies that this field only accepts strings as value
        30                                              # Verifies that this field only accepts strings as value
    ]
)
def test_users_put_validators(api_client, create_users, email, username, password):
    user = create_users()[0]
    url = "http://localhost:8000/api/users"
    data = {}

    if email is not None:
        data["email"] = email

    if username is not None:
        data["username"] = username

    if password is not None:
        data["password"] = password

    response = api_client.put(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    if (email == 'test@test.com') and (username == 'test') and (password == 'password'):
        assert response.status_code == status.HTTP_200_OK
        # The authenticated user does not have the old credentials anymore
        assert not User.objects.filter(id=user.id, username=user.username, email=user.email).exists()
        assert not AppUser.objects.filter(user__id=user.id, user__username=user.username, user__email=user.email).exists()
        # The authenticated user has the new credentials instead
        assert User.objects.filter(id=user.id, username=username, email=email).exists()
        assert AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
        assert "username" in response.data.keys()
        assert "email" in response.data.keys()
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_users_put_repeated_fields(api_client, create_users):
    url = "http://localhost:8000/api/users"

    k = random.randint(5, 10)
    users = create_users(k=k)
    i = random.randint(1, k-1)
    user = users[0]
    
    repeated_username = users[i].username
    repeated_email = users[i].email

    username = get_random_string(random.randint(6, 18))
    email = get_random_string(random.randint(6, 18))+'@test.com'
    password = 'updated-strong-password'
    # Repeated username
    data = {
        "username": repeated_username,
        "email": email,
        "password": password
    }

    response = api_client.put(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Repeated email
    data = {
        "username": username,
        "email": repeated_email,
        "password": password
    }

    response = api_client.put(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Repeated username, but it is the username of the authenticated user
    data = {
        "username": user.username,
        "email": email,
        "password": password
    }

    response = api_client.put(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_200_OK
    # Getting the user with the updated credentials
    user = User.objects.filter(id=user.id).first()
    # Repeated email, but it is the email of the authenticated user
    data = {
        "username": username,
        "email": user.email,
        "password": password
    }

    response = api_client.put(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'updated-strong-password'))

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_users_put_success(api_client, create_users):
    user = create_users()[0]
    url = "http://localhost:8000/api/users"

    username = get_random_string(random.randint(6, 18))
    email = get_random_string(random.randint(6, 18))+'@test.com'
    password = get_random_string(random.randint(6, 30))
    
    data = {
        "username": username,
        "email": email,
        "password": password
    }

    response = api_client.put(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_200_OK
    # The authenticated user does not have the old credentials anymore
    assert not User.objects.filter(id=user.id, username=user.username, email=user.email).exists()
    assert not AppUser.objects.filter(user__id=user.id, user__username=user.username, user__email=user.email).exists()
    # The authenticated user has the new credentials instead
    assert User.objects.filter(id=user.id, username=username, email=email).exists()
    assert AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
    assert "username" in response.data.keys()
    assert "email" in response.data.keys()

@pytest.mark.django_db
def test_users_delete_success(api_client, create_users):
    user = create_users()[0]
    url = "http://localhost:8000/api/users"

    response = api_client.delete(url, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_scores_authentication_post(api_client):
    url = "http://localhost:8000/api/scores"

    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_scores_put_not_allowed(api_client):
    url = "http://localhost:8000/api/scores"

    response = api_client.put(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_scores_delete_not_allowed(api_client):
    url = "http://localhost:8000/api/scores"

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_scores_get(api_client, scores):
    url = "http://localhost:8000/api/scores"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    score = response.data[0]
    assert "user" in score.keys()
    assert "game" in score.keys()
    assert "score" in score.keys()
    assert "date" in score.keys()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'score', [
        None,                                       # Verifies that this field is required
        random.randint(100, 500),
        True,                                       # Verifies that this field only accepts integers as value
        False,                                      # Verifies that this field only accepts integers as value
        get_random_string(random.randint(1, 30)),   # Verifies that this field only accepts integers as value
        35.5                                        # Verifies that this field only accepts integers as value
    ]
)
@pytest.mark.parametrize(
    'game_id', [
        random.randint(1, 3),
        None,                                       # Verifies that this field is required
        random.randint(4, 100),                     # Non existing game id
        True,                                       # Verifies that this field only accepts integers as value
        False,                                      # Verifies that this field only accepts integers as value
        get_random_string(random.randint(1, 30)),   # Verifies that this field only accepts integers as value
        35.5                                        # Verifies that this field only accepts integers as value
    ]
)
def test_scores_post_bad_request(api_client, create_users, games, score, game_id):
    nb_scores = Score.objects.count()

    user = create_users(k=1)[0]
    url = "http://localhost:8000/api/scores"
    data = {}

    if score is not None:
        data["score"] = score

    if game_id is not None:
        data["game"] = game_id

    response = api_client.post(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    if (type(score) is int) and (type(game_id) is int) and (1 <= game_id <= 3):
        assert response.status_code == status.HTTP_201_CREATED
        assert Score.objects.count() == nb_scores + 1
        assert Score.objects.filter(score=score, game__id=game_id).exists()
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    'score, game_id', [
        (random.randint(100, 500), random.randint(1, 3)),
    ]
)
def test_scores_post_success(api_client, create_users, games, score, game_id):
    nb_scores = Score.objects.count()
    
    user = create_users(k=1)[0]
    url = "http://localhost:8000/api/scores"
    data = {}

    if score is not None:
        data["score"] = score

    if game_id is not None:
        data["game"] = game_id

    response = api_client.post(url, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, 'strong-password'))

    assert response.status_code == status.HTTP_201_CREATED
    assert Score.objects.count() == nb_scores + 1
    assert Score.objects.filter(score=score, game__id=game_id).exists()


@pytest.mark.django_db
def test_games_get(api_client, games):
    url = "http://localhost:8000/api/games"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    game = response.data[0]
    assert "game_tag" in game.keys()
    assert "game_name" in game.keys()


@pytest.mark.django_db
def test_games_post_not_allowed(api_client):
    url = "http://localhost:8000/api/games"

    response = api_client.post(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_games_put_not_allowed(api_client):
    url = "http://localhost:8000/api/games"

    response = api_client.put(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_games_delete_not_allowed(api_client):
    url = "http://localhost:8000/api/games"

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_ads_get(api_client, ads):
    url = "http://localhost:8000/api/ads"

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    ad = response.data[0]
    assert "title" in ad.keys()
    assert "description" in ad.keys()
    assert "picture" in ad.keys()


@pytest.mark.django_db
def test_ads_post_not_allowed(api_client):
    url = "http://localhost:8000/api/ads"

    response = api_client.post(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_ads_put_not_allowed(api_client):
    url = "http://localhost:8000/api/ads"

    response = api_client.put(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_ads_delete_not_allowed(api_client):
    url = "http://localhost:8000/api/ads"

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED