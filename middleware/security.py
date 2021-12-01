import json
from application_services.user_resource import UserResource
from application_services.address_resource import AddressResource


WHITELISTED_PATHS = {"/test-insecure"}  # paths that do not require login


def check_path():
    result_pass = False
    if request.path in WHITELISTED_PATHS:  # no need for checking google-auth status
        result_pass = True
    else:
        token = request.headers["Authorization"][7:]
        payload = verify_auth_token(token)
        user_id = payload["user_id"]
        user = UserResource.get_by_user_id(user_id)
        if user:  # this user exist in db, i.e.
            print("'user_id': {}".format(user))
            return True
        else: # does it mean it has not logged in and need to do it?
            auth_with_google()
    return result_pass


    # 1. read token from request header
    # 2. verify token (deserialize -> {"user_id": ...})
    # 3. user_id in DB
    # return False


