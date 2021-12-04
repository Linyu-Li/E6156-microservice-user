from application_services.user_resource import UserResource

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

SECRET_KEY = '871d1670d6394a5572849e26c2decaee'

WHITELISTED_PATHS = {'/api/users', '/api/auth', '/api/auth-google', "/api/addresses"}  # paths that do not require login

expiration = 36000
serializer = Serializer(SECRET_KEY, expires_in=expiration)


def generate_auth_token(payload: dict) -> str:
    token = serializer.dumps(payload)
    return token.decode('ascii')


# Deserialize token
def verify_auth_token(token: str) -> dict:
    try:
        data = serializer.loads(token.encode('ascii'))
        return data  # ['user_id']
    except (SignatureExpired, BadSignature) as e:
        # print(e)
        return None


def check_path(request):
    """
    If a requested path is in the dict, the security implementation allows the request to proceed.
    """
    if request.path in WHITELISTED_PATHS:  # no need for checking google-auth status
        return True
    else:  # check if the user is logged in
        token = request.headers.get("Authorization")  # None if not logged in
        if token is not None:  # logged in
            token = token[7:]
            payload = verify_auth_token(token)
            # if payload is None:
            #     return False
            user_id = payload["userID"]
            if not UserResource.exists_by_email(payload['email']):
                return False
            user = UserResource.get_by_user_id(user_id)
            # double checking if the user is in db
            if user:
                # print("'user_id': {}".format(user))
                return True
            else:
                # print("'user_id': {} not exists".format(user))
                return False
        else:  # not logged in, redirect to Google to logged in
            return False
