import time
import pytest

from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from random import randint
from django.contrib.auth.models import User
from carcontrollerserver.models import AppUser, Game, Score
from carcontrollerserver.tests.conftest import get_random_string


class TestsSelenium:

    pausing_time = None

    def pause(self):
        if self.pausing_time is not None:
            time.sleep(self.pausing_time)

    def fill_login_form(self, driver, username, password):
        input_username = driver.find_element(By.ID, 'floatingInputUsername')
        input_password = driver.find_element(By.ID, 'floatingPassword')
        submit_button = driver.find_element(By.CLASS_NAME, 'btn-success')
        
        input_username.send_keys(username)
        input_password.send_keys(password)
        self.pause()    # Pause to see the form being filled
        submit_button.click()
        self.pause()    # Pause to see the result of the form submission

    def fill_account_form(self, driver, email, username, password, password_confirmation):
        input_email = driver.find_element(By.ID, 'floatingInputEmail')
        input_username = driver.find_element(By.ID, 'floatingInputUsername')
        input_password = driver.find_element(By.ID, 'floatingPassword')
        input_confirmation_password = driver.find_element(By.ID, 'floatingPasswordConfirmation')
        submit_button = driver.find_element(By.CLASS_NAME, 'btn-success')
        
        input_email.send_keys(email)
        input_username.send_keys(username)
        input_password.send_keys(password)
        input_confirmation_password.send_keys(password_confirmation)
        self.pause()    # Pause to see the form being filled
        submit_button.click()
        self.pause()    # Pause to see the result of the form submission

    def is_account_form_valid_in_HTML(self, driver):
        """
        Checks the validation of the form performed by the HTML itself
        
        Parameters:
        -   driver: Selenium driver object.

        Return:
        -   A boolean indicating if the data were validated by the HTML.
        """
        input_email = driver.find_element(By.ID, 'floatingInputEmail')
        input_username = driver.find_element(By.ID, 'floatingInputUsername')
        input_password = driver.find_element(By.ID, 'floatingPassword')
        input_confirmation_password = driver.find_element(By.ID, 'floatingPasswordConfirmation')
        
        return driver.execute_script("return arguments[0].checkValidity();", input_email) and\
                driver.execute_script("return arguments[0].checkValidity();", input_username) and\
                driver.execute_script("return arguments[0].checkValidity();", input_password) and\
                driver.execute_script("return arguments[0].checkValidity();", input_confirmation_password)

    def assert_menu(self, driver, is_authenticated):
        """
        Asserts if the menu has the expected items according to whether the user is authenticated. If the assertion
        fails, an exception is raised.

        Parameters:

        -   driver: Selenium driver object
        -   is_authenticated: boolean indicating if the user is authenticated

        """
        driver.find_element(By.ID, 'homeItem')
        driver.find_element(By.ID, 'rankingsItem')
        # This is the part of the menu content that varies according whether the user is authenticated 
        if is_authenticated:
            driver.find_element(By.ID, 'profileItem')
            driver.find_element(By.ID, 'logoutItem')
        else:
            driver.find_element(By.ID, 'signupItem')
            driver.find_element(By.ID, 'loginItem')

    def login_user(self, driver, live_server, user):
        """
        Fills the login form with valid data and authenticates. After a login, the browser user is redirected to 
        the dashboard webpage.
        
        Parameters

        -   driver: Selenium driver object
        -   live_server: Pytest live_server fixture
        -   user: Django model instance representing a user  
        """
        driver.get(live_server.url + "/account/login-form")
        self.pause()
        self.fill_login_form(driver, user.username, "strong-password")

    @pytest.mark.django_db
    def test_selenium_dashboard(self, driver, live_server, ads):
        "Tests dashboard access"
        driver.get(live_server.url + "/dashboard")
        carousel_ads = driver.find_elements(By.ID, 'carouselAds')
        carousel_items = driver.find_elements(By.CLASS_NAME, 'carousel-item')
        self.pause()
        assert len(carousel_ads) == 1
        assert len(carousel_items) == len(ads)
        self.assert_menu(driver, False)

    @pytest.mark.django_db
    def test_selenium_successful_login(self, driver, live_server, create_users):
        "Tests successful login"
        users = create_users(k=randint(1, 10))
        user = users[randint(0, len(users)-1)]
        driver.get(live_server.url + "/account/login-form")
        self.pause()
        # Fills the login form with valid data and authenticates
        self.fill_login_form(driver, user.username, "strong-password")

        carousel_ads = driver.find_elements(By.ID, 'carouselAds')
        greeting = driver.find_element(By.ID, 'greeting')

        assert driver.current_url == live_server.url + '/dashboard'
        assert len(carousel_ads) == 1
        assert greeting.text == "Welcome back, " + user.username
        self.assert_menu(driver, True)
        # Logout user
        driver.get(live_server.url + "/account/logout")

    @pytest.mark.django_db
    @pytest.mark.parametrize(
    'username, password', [
        (get_random_string(randint(6, 12)), get_random_string(randint(6, 30))),
        ('', get_random_string(randint(6, 30))),
        (get_random_string(randint(6, 12)), '')
        ]
    )
    def test_selenium_fail_login(self, driver, live_server, create_users, username, password):
        """Tests the case where the login fails due to wrong credentials"""
        create_users(k=randint(0, 10))
        # Fills the login form with invalid data
        driver.get(live_server.url + "/account/login-form")
        self.pause()
        self.fill_login_form(driver, username, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')

        assert driver.current_url == live_server.url + '/account/login-form'
        assert alert_danger.text == "Wrong credentials"
        self.assert_menu(driver, False)

    @pytest.mark.django_db
    def test_selenium_successful_signup(self, driver, live_server):
        """Tests successful signup"""
        # Fills the signup form with valid data
        driver.get(live_server.url + "/account/signup-form")
        self.pause()
        email = get_random_string(randint(6, 18))+"@test.com"
        username = get_random_string(randint(6, 18))
        password = get_random_string(randint(6, 30))
        self.fill_account_form(driver, email, username, password, password)

        alert_success = driver.find_element(By.CLASS_NAME, 'alert-success')
        # Checks that a new user was created
        assert User.objects.filter(email=email,username=username).exists()
        assert AppUser.objects.filter(user__email=email,user__username=username).exists()
        assert driver.current_url == live_server.url + '/account/signup-form'
        assert alert_success.text ==  "Account successfully created"
        self.assert_menu(driver, False)

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
    def test_selenium_fail_validation_signup(self, driver, live_server, email, username, password, password_confirmation):
        """Tests several cases where the email, username and password does not respect the business constaints"""
        if (email != 'test@test.com') or (username != 'test') or (password != 'password') or (password_confirmation != 'password'):
            # Fills the signup form with invalid data
            driver.get(live_server.url + "/account/signup-form")
            self.pause()
            self.fill_account_form(driver, email, username, password, password_confirmation)

            alerts_danger = driver.find_elements(By.CLASS_NAME, 'alert-danger')
            
            assert driver.current_url == live_server.url + '/account/signup-form'
            assert len(alerts_danger) > 0 or not(self.is_account_form_valid_in_HTML(driver))
            self.assert_menu(driver, False)
    
    @pytest.mark.django_db
    def test_selenium_repeated_fields_signup(self, driver, live_server, create_users):
        """Tests the signup fail due to repeated username and email"""
        users = create_users(k=randint(1, 10))
        user = users[randint(0, len(users) - 1)]
        # Fills the signup form with repeated username and email
        driver.get(live_server.url + "/account/signup-form")
        self.pause()
        password = get_random_string(randint(6, 30))
        username = user.username
        email = user.email
        self.fill_account_form(driver, email, username, password, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')
        
        assert driver.current_url == live_server.url + '/account/signup-form'
        assert alert_danger.text == "This username is not available"
        self.assert_menu(driver, False)
        # Fills the signup form with repeated email
        driver.get(live_server.url + "/account/signup-form")
        self.pause()
        password = get_random_string(randint(6, 30))
        username = get_random_string(randint(6, 18))
        email = user.email
        self.fill_account_form(driver, email, username, password, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')
        
        assert driver.current_url == live_server.url + '/account/signup-form'
        assert alert_danger.text == "This email is not available"
        self.assert_menu(driver, False)
        # Fills the signup form with repeated username
        driver.get(live_server.url + "/account/signup-form")
        self.pause()
        password = get_random_string(randint(6, 30))
        username = user.username
        email =  get_random_string(randint(6, 18)) + "@test.com"
        self.fill_account_form(driver, email, username, password, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')
        
        assert driver.current_url == live_server.url + '/account/signup-form'
        assert alert_danger.text == "This username is not available"
        self.assert_menu(driver, False)

    @pytest.mark.django_db
    def test_selenium_profile(self, driver, live_server, create_users):
        """Tests the access to the profile page by an authenticated user"""
        user = create_users()[0]
        self.login_user(driver, live_server, user)
        driver.get(live_server.url + "/account/profile")

        email_info = driver.find_element(By.ID, 'emailInfo')
        username_info = driver.find_element(By.ID, 'usernameInfo')

        assert email_info.text == "Email: " + user.email
        assert username_info.text == "Username: " + user.username
        self.assert_menu(driver, True)
        # Logout user
        driver.get(live_server.url + "/account/logout")

    @pytest.mark.django_db
    def test_selenium_successful_update_account(self, driver, live_server, create_users):
        """Tests the update of the account credentials"""
        user = create_users()[0]
        self.login_user(driver, live_server, user)
        # Fills the update form with valid data
        driver.get(live_server.url + "/account/update-form")
        self.pause()
        email = get_random_string(randint(6, 18))+"@test.com"
        username = get_random_string(randint(6, 18))
        password = get_random_string(randint(6, 30))
        self.fill_account_form(driver, email, username, password, password)

        email_info = driver.find_element(By.ID, 'emailInfo')
        username_info = driver.find_element(By.ID, 'usernameInfo')

        assert driver.current_url == live_server.url + "/account/profile"
        # Verify if the concerned user fields were really updated
        user_updated = User.objects.get(pk=user.id)
        assert user_updated.username == username
        assert user_updated.email == email
        # Verify if the updated data is shown
        assert email_info.text == "Email: " + email
        assert username_info.text == "Username: " + username
        self.assert_menu(driver, True)
        # Logout user
        driver.get(live_server.url + "/account/logout")

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
    def test_selenium_fail_validation_update_account(self, driver, live_server, create_users, email, username, password, password_confirmation):
        """Tests the cases where the account update fails due to a validation error"""
        if (email != 'test@test.com') or (username != 'test') or (password != 'password') or (password_confirmation != 'password'):
            user = create_users()[0]
            self.login_user(driver, live_server, user)
            # Fills the update form with valid data
            driver.get(live_server.url + "/account/update-form")
            self.pause()
            self.fill_account_form(driver, email, username, password, password_confirmation)

            alerts_danger = driver.find_elements(By.CLASS_NAME, 'alert-danger')

            assert driver.current_url == live_server.url + "/account/update-form"
            assert len(alerts_danger) > 0 or not(self.is_account_form_valid_in_HTML(driver))
            self.assert_menu(driver, True)
            # Logout user
            driver.get(live_server.url + "/account/logout")

    @pytest.mark.django_db
    def test_selenium_repeated_fields_update_account(self, driver, live_server, create_users):
        """Tests the cases where the account update fails due to a username or an email already in use"""
        users = create_users(k=randint(2,5))
        authenticated_user = users[0]
        user = users[randint(1, len(users)-1)]
        self.login_user(driver, live_server, authenticated_user)
        # Fills the update form with an email and a username in use
        driver.get(live_server.url + "/account/update-form")
        self.pause()
        new_email = get_random_string(randint(6, 18))+"@test.com"
        new_username = get_random_string(randint(6, 18))
        password = get_random_string(randint(6, 30))
        self.fill_account_form(driver, user.email, user.username, password, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')

        assert driver.current_url == live_server.url + "/account/update-form"
        assert alert_danger.text == "This username is not available"
        self.assert_menu(driver, True)
        # Fills the update form with a username in use    
        self.fill_account_form(driver, new_email, user.username, password, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')

        assert driver.current_url == live_server.url + "/account/update-form"
        assert alert_danger.text == "This username is not available"
        self.assert_menu(driver, True)
        # Fills the update form with an email in use    
        self.fill_account_form(driver, user.email, new_username, password, password)

        alert_danger = driver.find_element(By.CLASS_NAME, 'alert-danger')

        assert driver.current_url == live_server.url + "/account/update-form"
        assert alert_danger.text == "This email is not available"
        self.assert_menu(driver, True)
        # Logout user
        driver.get(live_server.url + "/account/logout")

    @pytest.mark.django_db
    def test_selenium_delete_account(self, driver, live_server, create_users):
        """Tests the deletion of an account"""
        user = create_users()[0]
        self.login_user(driver, live_server, user)
        driver.get(live_server.url + "/account/profile")
        self.pause()
        delete_button = driver.find_element(By.CLASS_NAME, "btn-danger")
        delete_button.click()
        self.pause()
        confirm_button = driver.find_element(By.ID, "confirmButton")
        driver.execute_script("arguments[0].click();", confirm_button)
        self.pause()
        # Waits the script to be executed (when it is executed, the redirect is performed)
        counter = 0
        while driver.current_url != live_server.url + "/dashboard":
            time.sleep(1)
            counter += 1
            if counter > 60:
                break
        assert driver.current_url == live_server.url + "/dashboard"
        assert not User.objects.filter(id=user.id).exists()
        assert not AppUser.objects.filter(user__id=user.id).exists()

    @pytest.mark.django_db
    @pytest.mark.parametrize('filename, is_successful', [
        ('C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\car-controller-app\\requirements.txt', False),
        ('C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\car-controller-app\\application\\static\\logo.png', True),
        (None, True)
    ])
    def test_selenium_change_picture(self, driver, live_server, create_users, filename, is_successful):
        """Tests the submission of the form used to change the profile picture with various inputs"""
        user = create_users()[0]
        self.login_user(driver, live_server, user)
        initial_profile_picture = AppUser.objects.get(user=user).picture
        driver.get(live_server.url + "/account/profile")
        self.pause()
        if filename is not None:
            picture_uploader = driver.find_element(By.ID, "id_picture")
            picture_uploader.send_keys(filename)
        submit_button = driver.find_element(By.ID, "buttonChangeProfilePicture")
        submit_button.click()
        self.pause()
        
        final_profile_picture = AppUser.objects.get(user=user).picture

        if not is_successful:
            alert_danger = driver.find_element(By.CLASS_NAME, "alert-danger")
            # Asserting that a format error happened
            assert alert_danger.text == "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
            # If an error happened, the picture must keep the same
            assert initial_profile_picture == final_profile_picture
        else:
            alerts_danger = driver.find_elements(By.CLASS_NAME, "alert-danger")
            # Asserting that no error happened
            assert len(alerts_danger) == 0
            if filename is None:
                # Asserting that the picture field keeps None
                assert not final_profile_picture
            else:
                # Asserting that the picture field is not None
                assert final_profile_picture
        self.assert_menu(driver, True)
        # Logout user
        driver.get(live_server.url + "/account/logout")

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'game_filter', [
            'driving_game',
            'obstacle_game',
            'parking_game',
            None
        ]
    )
    def test_selenium_profile_game_filters(self, driver, live_server, scores, game_filter):
        """Test the filters on the score games shown on the profile page"""
        users = User.objects.filter()
        user = users[0]
        self.login_user(driver, live_server, user)
        url = live_server.url + "/account/profile"
        if game_filter is not None:
            get_parameters = urlencode({'game': game_filter})    
            url = '{}?{}'.format(url, get_parameters)
        driver.get(url)

        username_info = driver.find_element(By.ID, "usernameInfo")
        email_info = driver.find_element(By.ID, "emailInfo")
        selected_option = driver.find_element(By.ID, "gameFilterField")
        score_game_names = driver.find_elements(By.ID, "scoreGameName")
        score_dates = driver.find_elements(By.ID, "scoreDate")
        score_values = driver.find_elements(By.ID, "scoreValue")
        # Testing if the user info are shown
        assert username_info.text == "Username: " + user.username
        assert email_info.text == "Email: " + user.email
        
        if game_filter is not None:
            game = Game.objects.filter(game_tag=game_filter).first()
            scores = Score.objects.filter(user=user, game__game_tag=game_filter)
        else:
            game = Game.objects.first()
            scores = Score.objects.filter(user=user, game=game)

        for i in range(len(score_game_names)):
            # Checking if the correct game name is shown
            assert score_game_names[i].text == game.game_name
        # Checks if the correct option is selected in the game filter field
        assert selected_option.text == game.game_name

        for i in range(len(score_game_names)):
            # Checking details of each score
            assert score_game_names[i].text == scores[i].game.game_name
            assert score_dates[i].text == scores[i].date.strftime("%Y/%m/%d %H:%M:%S %p")
            assert score_values[i].text == str(scores[i].score)

        assert len(score_game_names) == len(scores)
        assert len(score_dates) == len(scores)
        assert len(score_values) == len(scores)
        self.assert_menu(driver, True)
        
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
    def test_selenium_authenticated_endpoints(self, driver, live_server, url):
        """Tests the access of the endpoints that require authentication without a logged user"""
        driver.get(live_server.url + url)
        self.pause()
        # Asserts that the user is redirected to the login form
        assert driver.current_url == live_server.url + "/account/login-form"
        self.assert_menu(driver, False)
    
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'game_filter', [
            'driving_game',
            'obstacle_game',
            'parking_game',
            None
        ]
    )
    def test_selenium_rankings(self, driver, live_server, scores, game_filter):
        """Tests the game filter on the rankings page"""
        url = live_server.url + "/rankings"
        if game_filter is not None:
            get_parameters = urlencode({'game': game_filter})    
            url = '{}?{}'.format(url, get_parameters)
        driver.get(url)

        selected_option = driver.find_element(By.ID, "gameFilterField")
        score_positions = driver.find_elements(By.ID, "scorePosition")
        score_users = driver.find_elements(By.ID, "scoreUser")
        score_values = driver.find_elements(By.ID, "scoreValue")

        last_value = None
        users_dict = {}
        if game_filter is not None:
            # Checks if the correct option is selected in the game filter field
            assert selected_option.text == Game.objects.get(game_tag=game_filter).game_name
        else:
            # If no filter is specified, the first game must be selected
            assert selected_option.text == Game.objects.first().game_name
        for i in range(len(score_positions)):
            assert score_positions[i].text == str(i + 1)
            if i > 0:
                # The score values must be in the increasing order
                assert int(score_values[i].text) >= last_value
                # Each user must appear only once
                assert users_dict.get(score_users[i].text) is None
            last_value = int(score_values[i].text)
            users_dict[score_users[i].text] = True
        self.assert_menu(driver, False)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        'is_authenticated', [
            True,
            False
        ]
    )
    def test_selenium_logout(self, driver, live_server, create_users, is_authenticated):
        """Tests logout endpoint"""
        if is_authenticated:
            user = create_users()[0]
            self.login_user(driver, live_server, user)
        driver.get(live_server.url + "/account/logout")

        greetings = driver.find_elements(By.ID, "greeting")

        assert driver.current_url == live_server.url + "/dashboard"
        assert len(greetings) == 0
        self.assert_menu(driver, False)
