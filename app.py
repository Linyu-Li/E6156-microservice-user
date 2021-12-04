from flask import Flask, Response, request, jsonify, redirect, url_for
from flask_cors import CORS, cross_origin
import json
import logging
import os
from random import choice
import requests
import string

from flask_dance.contrib.google import make_google_blueprint, google

from application_services.user_resource import UserResource
from application_services.address_resource import AddressResource
import middleware.security as security

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

app.config['SECRET_KEY'] = security.SECRET_KEY
app.config['CORS_HEADERS'] = 'Content-Type'
client_id = "1093327178993-kbj68ghvsopafunmdk8rt1r6upt0oqdo.apps.googleusercontent.com"
client_secret = "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"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")
google_blueprint = app.blueprints.get("google")
PWD_CHARS = string.ascii_letters + string.digits + '!@#$%^&*()'

CORS(app,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     supports_credentials=True)


def generate_random_password():
    return ''.join(choice(PWD_CHARS) for _ in range(12))


@app.route('/api/me', methods=['GET'])
def get_current_user():
    token = request.headers["Authorization"][7:]
    payload = security.verify_auth_token(token)
    user_id = payload["user_id"]
    user = UserResource.get_by_user_id(user_id)
    if user:
        return Response(json.dumps({'user_id': user_id}, default=str), status=200, content_type="application/json")
    return Response("Invalid token", status=401, content_type="text")


@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':  # create user
        req_data = request.get_json()
        email = req_data.get('email', None)
        if email is None:
            return Response(json.dumps("Email missing.", default=str), status=400, content_type="application/json")
        if UserResource.exists_by_email(email):
            return Response(json.dumps("Email already registered. Please login or use another email.", default=str),
                            status=422, content_type="application/json")
        # TODO encode password
        if req_data.get('password', None) is None:
            return Response(json.dumps("Password missing.", default=str), status=400, content_type="application/json")

        data = {}
        for k in req_data:
            if req_data[k] is not None:
                # TODO check if data contains keys that do not correspond to any columns on the DB table
                data[k] = req_data[k]
        column_name_list = []
        value_list = []
        for key, value in data.items():
            column_name_list.append(key)
            value_list.append(value)
        usr_id = UserResource.insert_users(column_name_list, value_list)
        rsp = Response(
            json.dumps(
                f"User registered with userID {usr_id} (for debug only, do NOT show this in production!)", default=str),
            status=201, content_type="application/json")
        return rsp
    elif request.method == 'GET':
        res = UserResource.get_all_users()
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=405, content_type="application/json")


@app.route('/api/auth', methods=['POST'])
def auth():
    if request.method != 'POST':
        return Response(json.dumps("method not allowed", default=str), status=405, content_type="application/json")
    req_data = request.get_json()
    email, pwd = req_data['email'], req_data['password']
    user_info = UserResource.get_user_info_by_email_pwd(email, pwd)
    if user_info is None:
        return Response(json.dumps("incorrect email and/or password.", default=str),
                        status=401, content_type="application/json")
    token = security.generate_auth_token({'userID': user_info['userID'], 'email': user_info['email']})
    return jsonify({'token': '{}'.format(token), 'user': user_info})


@app.route('/api/auth-google', methods=['GET'])
def auth_with_google():
    req_data = request.get_json()
    email = req_data.get("email")
    user_id = UserResource.get_user_id_by_email(email)
    if user_id is None:
        user_id = UserResource.insert_users(
            ['email', 'nameFirst', 'nameLast', 'password'],
            [email,
             req_data.get('given_name', None),
             req_data.get('family_name', None),
             generate_random_password()])
    # TODO may generate token with a more complicated payload
    token = security.generate_auth_token({'userID': user_id, 'email': email})
    return jsonify({'token': 'Bearer {}'.format(token)})

# @app.route('/api/auth-google', methods=['GET'])
# def auth_with_google():
#     if google.authorized:
#         user_data = google.get('oauth2/v2/userinfo').json()
#         # token = blueprint.session.token
#         email = user_data['email']
#         user_id = UserResource.get_user_id_by_email(email)
#         if user_id is None:
#             user_id = UserResource.insert_users(
#                 ['email', 'nameFirst', 'nameLast', 'password'],
#                 [email,
#                  user_data.get('given_name', None),
#                  user_data.get('family_name', None),
#                  generate_random_password()])
#         token = generate_auth_token({'user_id': user_id})   # TODO may generate token with a more complicated payload
#         return jsonify({'token': 'Bearer {}'.format(token.decode("utf-8"))})
#     return redirect(url_for('google.login'))


@app.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_user(user_id):
    if request.method == 'GET':  # retrieve user info
        fields = request.args.get('fields', 'nameFirst,nameLast,email,addressID,gender').split(',')
        try:
            res = UserResource.get_by_user_id(user_id, fields)
        except:
            return Response(json.dumps("Invalid fields requested!", default=str),
                            status=422, content_type="application/json")
        if res:
            res = res[0]
            res.pop('password', None)
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        else:
            rsp = Response(json.dumps(f"User with ID {user_id} not found!", default=str),
                           status=404, content_type="application/json")
        return rsp

    elif request.method == 'PUT':
        req_data = request.get_json()

        # Original: update user info, currently only support modifying one column at a time
        # column_name = list(req_data.items())[0][0]
        # value = list(req_data.items())[0][1]
        # res = UserResource.update_field_by_uid(user_id, column_name, value)

        # New: update user info multiple columns at a time
        UserResource.update_fields_by_uid(user_id, **req_data)

        rsp = Response(json.dumps("Updated", default=str), status=200, content_type="application/json")
        return rsp

    elif request.method == 'DELETE':  # delete user
        res = UserResource.delete_by_uid(user_id)
        rsp = Response(json.dumps("Deleted", default=str), status=204, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=405, content_type="application/json")


@app.route('/api/users/<user_id>/weather', methods=['GET'])
def get_weather(user_id):
    user = UserResource.get_by_user_id(user_id)
    address_id = str(user[0]['addressID'])
    address = AddressResource.get_by_address_id(address_id)
    zip_code = int(address[0]['postalCode'])

    api_key = "e77746cf4f104a79a0e834cb44c84522"
    api_url = f"https://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&units=imperial&appid={api_key}"
    res = requests.get(api_url).json()

    current_weather = res['weather'][0]['main']
    current_temperature = "{0:.2f}".format(res["main"]["temp"])
    name = res['name']
    cod = res['cod']

    weather = {
        'location': name,
        'current_weather': current_weather,
        'current_temperature': current_temperature
    }
    return Response(json.dumps(weather, default=str), status=cod, content_type="application/json")


@app.route('/api/address', methods=['GET', 'POST'])
def address():
    if request.method == 'POST':  # create address
        req_data = request.get_json()
        column_name_list = []
        value_list = []
        for key, value in req_data.items():
            column_name_list.append(key)
            value_list.append(value)
        res = AddressResource.insert_address(column_name_list, value_list)
        rsp = Response(json.dumps("Added address", default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'GET':
        res = AddressResource.get_all_addresses()
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=405, content_type="application/json")


@app.route('/api/address/<address_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_address(address_id):
    if request.method == 'GET':  # retrieve address info
        res = AddressResource.get_by_address_id(address_id)
        if res:
            rsp = Response(json.dumps(res[0], default=str), status=200, content_type="application/json")
        else:
            rsp = Response(json.dumps(f"Address with ID {address_id} not found!", default=str),
                           status=404, content_type="application/json")
        return rsp
    elif request.method == 'PUT':  # update address info, currently only support modifying one column at a time
        req_data = request.get_json()
        column_name = list(req_data.items())[0][0]
        value = list(req_data.items())[0][1]
        print(list(req_data.items()))
        res = AddressResource.update_by_aid(address_id, column_name, value)
        rsp = Response(json.dumps("Updated", default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'DELETE':  # delete address
        res = AddressResource.delete_by_aid(address_id)
        rsp = Response(json.dumps("Deleted", default=str), status=204, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=405, content_type="application/json")


@app.before_request
def check_valid_path():
    print("check_valid_path")
    print(request.path)
    result_pass = security.check_path(request)
    print("result_pass: {}".format(result_pass))
    if not result_pass:
        print("path not in whitelist")

        # Deprecated plan: google oauth at back end
        # return redirect(url_for('google.login'))  # redirect to the frontend google auth page

        # New plan: return 401 unauthorized response if not result_pass
        # Problem: if return response here, front end complains no CORS
        # rsp = Response(json.dumps("not authorized", default=str), status=401, content_type="application/json")
        # rsp.headers.add("Access-Control-Allow-Origin", "*")
        # rsp.headers.add('Access-Control-Allow-Headers', "*")
        # rsp.headers.add('Access-Control-Allow-Methods', "*")
        # return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    # app.run(port=5000)
