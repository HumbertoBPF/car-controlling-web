from django.contrib.auth.models import User

def is_valid_user_data(email, username, password, password_confirmation, existing_user=None):
    '''Validates user credentials. This method is typically called before creation and updates with respect to the User model.
    The validations that are performed are:\n
    
    - Verifies if the all the fields are non empty\n
    - Verifies if the fields contain spaces(spaces characters are forbidden)\n
    - Verifies if the specified email and username are available since they are unique fields\n
    - Verifies if the specified password has a length between 6 and 30\n
    - Verifies if the password was correctly confirmed\n
    
    A optional argument "existing_user" can be provided. For such a case, it is allowed to use a username and an email that 
    are associated with an existing user since they match with the specified "existing_user" argument.\n
    
    The return values are a boolean indicating if the provided data is valid and two strings with the validation error and 
    the field concerned in case of validation error.'''
    error_msg = ""
    error_field = ""
    
    if " " in email:
        error_msg = "Fields cannot contain spaces"
        error_field = "email"
        return False, error_msg, error_field
    
    if " " in username:
        error_msg = "Fields cannot contain spaces"
        error_field = "username"
        return False, error_msg, error_field
    
    if " " in password:
        error_msg = "Fields cannot contain spaces"
        error_field = "password"
        return False, error_msg, error_field
    
    if len(email) == 0:
        error_msg = "All fields are required"
        error_field = "email"
        return False, error_msg, error_field
    
    if len(username) == 0:
        error_msg = "All fields are required"
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
        error_msg = "Password length out of range(passwords must be 6 and 30 characters long)"
        error_field = "password"
        return False, error_msg, error_field
    
    if password != password_confirmation:
        error_msg = "The passwords do not match"
        error_field = "password"
        return False, error_msg, error_field

    return True, error_msg, error_field