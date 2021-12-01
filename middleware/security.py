import json


WHITELISTED_PATHS = {"/test-insecure"}  # paths that do not require login

@app.before_request
def check_path(request):
    if request.path not in WHITELISTED_PATHS:
        # check if the user is logged in
        token = request.headers["Authorization"][7:]
        payload = verify_auth_token(token)
        user_id = payload["user_id"]
        user = UserResource.get_by_user_id(user_id)
        if user:
            return Response(json.dumps({'user_id': user_id}, default=str), status=200, content_type="application/json")
        return Response("Invalid token", status=401, content_type="text")
    
    # 1. read token from request header
    # 2. verify token (deserialize -> {"user_id": ...})
    # 3. user_id in DB
    return False
