# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.a_Domain.OrderService import *

# Decorator Imports #
from src.e_Infra.f_Decorators.JsonLoadsDecorator import *


# /order route #
@app_handler.route('/order', methods=['GET'])
def order_route_get():
    # Routing request to /order GET method #
    if request.method == 'GET':
        result = get_order_set(
            request.args.to_dict(), {'HTTP_SELECT': request.environ.get('HTTP_SELECT'),
                                     'HTTP_ORDERBY': request.environ.get('HTTP_ORDERBY'),
                                     'HTTP_LIMIT': request.environ.get('HTTP_LIMIT'),
                                     'HTTP_PAGE': request.environ.get('HTTP_PAGE')}
        )
        return result


# /order route #
@app_handler.route('/order', methods=['POST', 'PATCH', 'PUT'])
def order_route_post_patch_put():
    # Routing request to /order POST method #
    if request.method == 'POST':
        result = post_order_set(request.json)
        return result
    # Routing request to /order PATCH method #
    if request.method == 'PATCH':
        result = patch_order_set(request.json)
        return result
    if request.method == 'PUT':
        result = put_order_set(request.json)
        return result


# /order route #
@app_handler.route('/order', methods=['DELETE'])
def order_route_delete_by_full_match():
    # Routing request to /order DELETE method #
    if request.method == 'DELETE':
        result = delete_order_by_full_match(request.json)
        return result


# /order/{id} route #
@app_handler.route('/order/<id_order>', methods=['GET'])
def order_route_get_by_id(id_order):
    # Routing request to /order/{id} GET method #
    if request.method == 'GET':
        result = get_order_by_id(
            [id_order], request.args.to_dict(
            ), {'HTTP_SELECT': request.environ.get('HTTP_SELECT')}
        )
        return result


# /order/{id} route #
@app_handler.route('/order/<id_order>', methods=['DELETE'])
def order_route_delete_by_id(id_order):
    # Routing request to /order/{id} DELETE method #
    if request.method == 'DELETE':
        result = delete_order_by_id([id_order])
        return result
