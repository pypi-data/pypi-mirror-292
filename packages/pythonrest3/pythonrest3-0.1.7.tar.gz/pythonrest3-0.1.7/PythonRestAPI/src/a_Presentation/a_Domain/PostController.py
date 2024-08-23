# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.a_Domain.PostService import *

# Decorator Imports #
from src.e_Infra.f_Decorators.JsonLoadsDecorator import *


# /post route #
@app_handler.route('/post', methods=['GET'])
def post_route_get():
    # Routing request to /post GET method #
    if request.method == 'GET':
        result = get_post_set(
            request.args.to_dict(), {'HTTP_SELECT': request.environ.get('HTTP_SELECT'),
                                     'HTTP_ORDERBY': request.environ.get('HTTP_ORDERBY'),
                                     'HTTP_LIMIT': request.environ.get('HTTP_LIMIT'),
                                     'HTTP_PAGE': request.environ.get('HTTP_PAGE')}
        )
        return result


# /post route #
@app_handler.route('/post', methods=['POST', 'PATCH', 'PUT'])
def post_route_post_patch_put():
    # Routing request to /post POST method #
    if request.method == 'POST':
        result = post_post_set(request.json)
        return result
    # Routing request to /post PATCH method #
    if request.method == 'PATCH':
        result = patch_post_set(request.json)
        return result
    if request.method == 'PUT':
        result = put_post_set(request.json)
        return result


# /post route #
@app_handler.route('/post', methods=['DELETE'])
def post_route_delete_by_full_match():
    # Routing request to /post DELETE method #
    if request.method == 'DELETE':
        result = delete_post_by_full_match(request.json)
        return result


# /post/{id} route #
@app_handler.route('/post/<id_post>', methods=['GET'])
def post_route_get_by_id(id_post):
    # Routing request to /post/{id} GET method #
    if request.method == 'GET':
        result = get_post_by_id(
            [id_post], request.args.to_dict(
            ), {'HTTP_SELECT': request.environ.get('HTTP_SELECT')}
        )
        return result


# /post/{id} route #
@app_handler.route('/post/<id_post>', methods=['DELETE'])
def post_route_delete_by_id(id_post):
    # Routing request to /post/{id} DELETE method #
    if request.method == 'DELETE':
        result = delete_post_by_id([id_post])
        return result
