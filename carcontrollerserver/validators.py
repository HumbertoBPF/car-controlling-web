from django.contrib.auth.models import User


def is_valid_user_data(email, username, password, password_confirmation, existing_user=None):
    """
    Validates user credentials. This method is typically called before creation and updates with respect to the User model.
    The validations that are performed are:

    - Verifies if the all the fields are non-empty
    - Verifies if the fields contain spaces(spaces characters are forbidden)
    - Verifies if the specified email and username are available since they are unique fields
    - Verifies if the specified password has a length between 6 and 30
    - Verifies if the password was correctly confirmed

    :param email: email to be validated
    :type email: str
    :param username: username to be validated
    :type username: str
    :param password: password to be validated
    :type password: str
    :param password_confirmation: password confirmation input
    :type password_confirmation: str
    :param existing_user: User that is going to be modified with the parameters above
    :type existing_user: User

    :return: tuple with a boolean indicating if the specified data is valid, a string with the error message in case
    of validation error and a string with the name of the first field that failed to be validated.
    """
    error_msg = ""
    error_field = ""
    
    if " " in email:
        error_msg = "Email cannot contain spaces"
        error_field = "email"
        return False, error_msg, error_field
    
    if " " in username:
        error_msg = "Username cannot contain spaces"
        error_field = "username"
        return False, error_msg, error_field
    
    if " " in password:
        error_msg = "Password cannot contain spaces"
        error_field = "password"
        return False, error_msg, error_field
    
    if len(email) == 0:
        error_msg = "Email is required"
        error_field = "email"
        return False, error_msg, error_field
    
    if len(username) == 0:
        error_msg = "Username is required"
        error_field = "username"
        return False, error_msg, error_field
    
    if User.objects.filter(username=username).exists() and ((existing_user is None) or (existing_user.username != username)):
        error_msg = "This username is not available"
        error_field = "username"
        return False, error_msg, error_field
    
    if User.objects.filter(email=email).exists() and ((existing_user is None) or (existing_user.email != email)):
        error_msg = "This email is not available"
        error_field = "email"
        return False, error_msg, error_field
    
    if len(password) < 6 or len(password) > 30:
        error_msg = "Password length out of range (passwords must be 6 and 30 characters long)"
        error_field = "password"
        return False, error_msg, error_field
    
    if password != password_confirmation:
        error_msg = "The passwords do not match"
        error_field = "password"
        return False, error_msg, error_field

    return True, error_msg, error_field
