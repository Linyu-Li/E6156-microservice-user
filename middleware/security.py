import json
from application_services.user_resource import UserResource
from application_services.address_resource import AddressResource


WHITELISTED_PATHS = {"/users", '/api/auth-google'}  # paths that do not require login


def check_path(request):
    '''
    If a request path is in the dict, the security implementation allows the request to proceed.
    '''
    if request.path in WHITELISTED_PATHS:  # no need for checking google-auth status
        return True
    else:  # check if the user is logged in
        token = request.headers.get("Authorization")  # None if not logged in
        if token is not None:  # logged in
            token = token[7:]
            payload = verify_auth_token(token)
            user_id = payload["user_id"]
            user = UserResource.get_by_user_id(user_id)
            # double checking if the user is in db
            if user:
                print("'user_id': {}".format(user))
                return True
            else:
                print("'user_id': {} not exists".format(user))
                return False
        else:  # not logged in, redirect to Google to logged in
            return False