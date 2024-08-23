# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.a_Domain.ProductService import *

# Decorator Imports #
from src.e_Infra.f_Decorators.JsonLoadsDecorator import *


# /product route #
@app_handler.route('/product', methods=['GET'])
def product_route_get():
    # Routing request to /product GET method #
    if request.method == 'GET':
        result = get_product_set(
            request.args.to_dict(), {'HTTP_SELECT': request.environ.get('HTTP_SELECT'),
                                     'HTTP_ORDERBY': request.environ.get('HTTP_ORDERBY'),
                                     'HTTP_LIMIT': request.environ.get('HTTP_LIMIT'),
                                     'HTTP_PAGE': request.environ.get('HTTP_PAGE')}
        )
        return result


# /product route #
@app_handler.route('/product', methods=['POST', 'PATCH', 'PUT'])
def product_route_post_patch_put():
    # Routing request to /product POST method #
    if request.method == 'POST':
        result = post_product_set(request.json)
        return result
    # Routing request to /product PATCH method #
    if request.method == 'PATCH':
        result = patch_product_set(request.json)
        return result
    if request.method == 'PUT':
        result = put_product_set(request.json)
        return result


# /product route #
@app_handler.route('/product', methods=['DELETE'])
def product_route_delete_by_full_match():
    # Routing request to /product DELETE method #
    if request.method == 'DELETE':
        result = delete_product_by_full_match(request.json)
        return result


# /product/{id} route #
@app_handler.route('/product/<id_product>', methods=['GET'])
def product_route_get_by_id(id_product):
    # Routing request to /product/{id} GET method #
    if request.method == 'GET':
        result = get_product_by_id(
            [id_product], request.args.to_dict(
            ), {'HTTP_SELECT': request.environ.get('HTTP_SELECT')}
        )
        return result


# /product/{id} route #
@app_handler.route('/product/<id_product>', methods=['DELETE'])
def product_route_delete_by_id(id_product):
    # Routing request to /product/{id} DELETE method #
    if request.method == 'DELETE':
        result = delete_product_by_id([id_product])
        return result
