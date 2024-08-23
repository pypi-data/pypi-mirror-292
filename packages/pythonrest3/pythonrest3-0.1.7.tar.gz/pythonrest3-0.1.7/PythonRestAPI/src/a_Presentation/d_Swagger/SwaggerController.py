# System imports #
import json
import yaml

# Flask Imports #
from flask import request
from src.e_Infra.b_Builders.FlaskBuilder import *


# /swaggerdata route #
@app_handler.route('/swaggerdata', methods=['GET'])
def swagger_route():
    # Routing request to /swaggerdata GET method #
    if request.method == 'GET':

        yaml_file = open("config/swagger.yaml")
        data = yaml.safe_load(yaml_file)
        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}


# /swaggerdata/order route #
@app_handler.route('/swaggerdata/order', methods=['GET'])
def swagger_route_order():
    # Routing request to /order GET method #
    if request.method == 'GET':

        yaml_file = open("config/Order.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}


# /swaggerdata/post route #
@app_handler.route('/swaggerdata/post', methods=['GET'])
def swagger_route_post():
    # Routing request to /post GET method #
    if request.method == 'GET':

        yaml_file = open("config/Post.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}


# /swaggerdata/product route #
@app_handler.route('/swaggerdata/product', methods=['GET'])
def swagger_route_product():
    # Routing request to /product GET method #
    if request.method == 'GET':

        yaml_file = open("config/Product.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}


# /swaggerdata/reservation route #
@app_handler.route('/swaggerdata/reservation', methods=['GET'])
def swagger_route_reservation():
    # Routing request to /reservation GET method #
    if request.method == 'GET':

        yaml_file = open("config/Reservation.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}


# /swaggerdata/settypetable route #
@app_handler.route('/swaggerdata/settypetable', methods=['GET'])
def swagger_route_settypetable():
    # Routing request to /settypetable GET method #
    if request.method == 'GET':

        yaml_file = open("config/SetTypeTable.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}


# /swaggerdata/user route #
@app_handler.route('/swaggerdata/user', methods=['GET'])
def swagger_route_user():
    # Routing request to /user GET method #
    if request.method == 'GET':

        yaml_file = open("config/User.yaml")
        data = yaml.safe_load(yaml_file)

        data['servers'] = [{"url": ''}]

        return json.dumps(data), 200, {'Content-Type': 'application/json'}
