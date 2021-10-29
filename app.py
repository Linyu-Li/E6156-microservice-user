from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import json
import logging
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from application_services.user_resource import UserResource
from application_services.address_resource import AddressResource

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = '871d1670d6394a5572849e26c2decaee'
CORS(app)


def generate_auth_token(user_id, expiration=36000):
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'user_id': user_id})


# Deserialize token
def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        return data
    except (SignatureExpired, BadSignature):
        return None


@app.route('/users', methods=['GET', 'POST'])
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
        rsp = Response(json.dumps("User registered with userID {} (for debug only, do NOT show this in production!)".format(usr_id),
                                  default=str),
                       status=200, content_type="application/json")
        return rsp
    elif request.method == 'GET':
        res = UserResource.get_all_users()
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=405, content_type="application/json")


@app.route('/auth', methods=['POST'])
def auth():
    if request.method != 'POST':
        return Response(json.dumps("method not allowed", default=str), status=405, content_type="application/json")
    req_data = request.get_json()
    email, pwd = req_data['email'], req_data['password']
    user_id = UserResource.get_user_id_by_email_pwd(email, pwd)     # TODO decode password if encoded
    if user_id is None:
        return Response(json.dumps("incorrect email and/or password.", default=str),
                        status=401, content_type="application/json")
    token = generate_auth_token(user_id)
    return jsonify({'token': 'Bearer {}'.format(token.decode("utf-8"))})


@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_user(user_id):
    if request.method == 'GET':  # retrieve user info
        res = UserResource.get_by_user_id(user_id)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'PUT':  # update user info, currently only support modifying one column at a time
        req_data = request.get_json()
        column_name = list(req_data.items())[0][0]
        value = list(req_data.items())[0][1]
        print(list(req_data.items()))
        res = UserResource.update_by_uid(user_id, column_name, value)
        rsp = Response(json.dumps("Updated", default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'DELETE':  # delete user
        res = UserResource.delete_by_uid(user_id)
        rsp = Response(json.dumps("Deleted", default=str), status=200, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=404, content_type="application/json")


@app.route('/address', methods=['GET', 'POST'])
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
        return Response(json.dumps("wrong method", default=str), status=404, content_type="application/json")


@app.route('/address/<address_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_address(address_id):
    if request.method == 'GET':  # retrieve address info
        res = AddressResource.get_by_address_id(address_id)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
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
        rsp = Response(json.dumps("Deleted", default=str), status=200, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=404, content_type="application/json")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
