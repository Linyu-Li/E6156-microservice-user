from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging

from application_services.user_resource import UserResource
from application_services.address_resource import AddressResource

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)



@app.route('/', methods = ['POST', 'GET', 'PUT'])
def hello_world():
    return '<u>Hello World!</u>'


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':  # create user
        req_data = request.get_json()
        column_name_list = []
        value_list = []
        for key, value in req_data.items():
            column_name_list.append(key)
            value_list.append(value)
        res = UserResource.insert_users(column_name_list, value_list)
        rsp = Response(json.dumps("Added user", default=str), status=200, content_type="application/json")
        return rsp
    elif request.method == 'GET':
        res = UserResource.get_all_users()
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp
    else:
        return Response(json.dumps("wrong method", default=str), status=404, content_type="application/json")


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
