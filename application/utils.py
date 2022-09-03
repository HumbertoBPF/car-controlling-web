def contains_parameters(request, *parameters):
    """
    Checks if the parameters specified are passed in the request

    :param request: dictionary corresponding to the request method concerned
    :param parameters: optional. Parameters that we want to search in the request

    :return: a boolean indicating if all the parameters specified are present in the request
    """
    for parameter in parameters:
        if request.get(parameter) is None:
            return False
    return True
