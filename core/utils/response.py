def success_response(data=None, message=None):
    return {
        'status': 'success',
        'data': data,
        'message': message,
    }


def error_response(errors):
    return {
        'status': 'error',
        'errors': errors,
    }
