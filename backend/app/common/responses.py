def success_response(message, data=None, status_code=200):
    response = {
        "success": True,
        "message": message
    }

    if data is not None:
        response["data"] = data

    return response, status_code


def error_response(message, status_code=400, data=None):
    response = {
        "success": False,
        "message": message
    }

    if data is not None:
        response["data"] = data

    return response, status_code