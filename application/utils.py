

def contains_parameters(request, *parameters):
    '''Checks if the parameters specified are passed in the request
    Parameters:

    request: dictionary corresponding to the request method concerned
    optional: parameters that we want to search in the request 

    return: boolean indicating if all the parameters specified are present in the request
    '''
    for parameter in parameters:
        print(parameter)
        if request.get(parameter) is None:
            return False
    return True
