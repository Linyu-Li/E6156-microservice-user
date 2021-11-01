import json


WHITELISTED_PATHS = {"/test-insecure"}


def check_path(request, oauth, blueprint):
    if request.path in WHITELISTED_PATHS or oauth.authorized:
        return True
    # if oauth.authorized:
        # info = 'oauth2/v2/userinfo'
        # data = oauth.get(info).json()
        # print(json.dumps(data, indent=2))
        # token = blueprint.session.token
        # print(json.dumps(token, indent=2))
        # return True
    return False
