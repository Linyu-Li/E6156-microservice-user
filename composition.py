from flask import Flask, Response, request
from flask_cors import CORS
import json
from requests_futures.sessions import FuturesSession
from typing import *

app = Flask(__name__)
CORS(app)
SESS = FuturesSession()

# TODO change apis below to AWS ones in deployment
USR_ADDR_PROPS = {
    'microservice': 'User/address microservice',
    'api': 'http://localhost:5001/users',
    'fields': ('nameLast', 'nameFirst', 'email', 'addressID', 'password', 'gender')
}
USR_PREF_PROPS = {
    'microservice': 'User profile microservice',
    'api': 'http://localhost:5002/profile',
    'fields': ('movie', 'hobby', 'book', 'music', 'sport', 'major', 'orientation')
}
SCHEDULE_PROPS = {
    'microservice': 'Scheduler microservice',
    'api': 'http://localhost:5003/availability',
    'fields': ('availID', )
}
PUT_PROPS = (
    USR_ADDR_PROPS,
    USR_PREF_PROPS,
    # SCHEDULE_PROPS
)


def project_req_data(req_data: dict, props: tuple) -> dict:
    res = dict()
    for prop in props:
        if prop not in req_data:
            return None
        res[prop] = req_data[prop]
    return res


def async_request_microservices(req_data: dict, data_ids: Tuple[str], headers: Dict) -> (int, str):
    # async_list = [None, None,]  # None]
    futures = []
    for i, put_prop in enumerate(PUT_PROPS):
        data = project_req_data(req_data, put_prop['fields'])
        if data is None:
            return 400, f"Missing data field(s) for {put_prop['microservice']}"
        futures.append(SESS.put(put_prop['api'] + f"/{data_ids[i]}", data=json.dumps(data), headers=headers))

    for i, future in enumerate(futures):
        res = future.result()
        if res is None:
            return 408, f"{PUT_PROPS[i]['microservice']} did not response."
        elif not res.ok:
            return res.status_code, \
                   f"Response from the {PUT_PROPS[i]['microservice']} is not OK."
    return 200, "User info updated successfully!"


@app.route('/api/update', methods=['PUT'])
def update_info():
    if request.method != 'PUT':
        status_code = 405
        return Response(f"{status_code} - wrong method!", status=status_code, mimetype="application/json")

    # TODO may replace IDs below with data decoded from access token instead
    args = request.args
    data_ids = (
        args.get('userID', None),
        args.get('profileID', None),
        # args.get('availID', None)
    )
    if any(d_id is None for d_id in data_ids):
        status_code = 400
        return Response(f"{status_code} - missing data IDs!", status=status_code, mimetype="application/json")
    req_data = request.get_json()
    status_code, message = async_request_microservices(req_data, data_ids, request.headers)
    return Response(f"{status_code} - {message}", status=status_code, mimetype="application/json")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
