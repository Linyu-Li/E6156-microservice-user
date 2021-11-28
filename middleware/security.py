import json


WHITELISTED_PATHS = {"/test-insecure"}  # paths that do not require login


def check_path(request):
    if request.path in WHITELISTED_PATHS:
        return True
    # 1. read token from request header
    # 2. verify token (deserialize -> {"user_id": ...})
    # 3. user_id in DB
    return False
