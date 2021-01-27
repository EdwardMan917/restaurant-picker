def get_restaurant_response_code(result: dict) -> int:

    status_codes = {
        'DB_CONNECTION_ERROR': 503,
        'COLLECTION_NOT_FOUND': 404,
        'INTERNAL_SERVER_ERROR': 500
    }

    error_code = result.get('error_code')

    return status_codes.get(error_code, 200)


def get_status_response_code(result: dict) -> int:

    status_codes = {
        'DB_CONNECTION_ERROR': 503,
        'COLLECTION_NOT_FOUND': 404,
        'INTERNAL_SERVER_ERROR': 500
    }
    error_code = result.get('error_code')

    return status_codes.get(error_code, 200)