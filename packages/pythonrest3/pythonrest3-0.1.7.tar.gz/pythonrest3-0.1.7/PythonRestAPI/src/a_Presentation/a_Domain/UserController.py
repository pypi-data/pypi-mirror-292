# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.a_Domain.UserService import *

# Decorator Imports #
from src.e_Infra.f_Decorators.JsonLoadsDecorator import *


# /user route #
@app_handler.route('/user', methods=['GET'])
def user_route_get():
    # Routing request to /user GET method #
    if request.method == 'GET':
        result = get_user_set(
            request.args.to_dict(), {'HTTP_SELECT': request.environ.get('HTTP_SELECT'),
                                     'HTTP_ORDERBY': request.environ.get('HTTP_ORDERBY'),
                                     'HTTP_LIMIT': request.environ.get('HTTP_LIMIT'),
                                     'HTTP_PAGE': request.environ.get('HTTP_PAGE')}
        )
        return result


# /user route #
@app_handler.route('/user', methods=['POST', 'PATCH', 'PUT'])
def user_route_post_patch_put():
    # Routing request to /user POST method #
    if request.method == 'POST':
        result = post_user_set(request.json)
        return result
    # Routing request to /user PATCH method #
    if request.method == 'PATCH':
        result = patch_user_set(request.json)
        return result
    if request.method == 'PUT':
        result = put_user_set(request.json)
        return result


# /user route #
@app_handler.route('/user', methods=['DELETE'])
def user_route_delete_by_full_match():
    # Routing request to /user DELETE method #
    if request.method == 'DELETE':
        result = delete_user_by_full_match(request.json)
        return result


# /user/{id} route #
@app_handler.route('/user/<id_user>', methods=['GET'])
def user_route_get_by_id(id_user):
    # Routing request to /user/{id} GET method #
    if request.method == 'GET':
        result = get_user_by_id(
            [id_user], request.args.to_dict(
            ), {'HTTP_SELECT': request.environ.get('HTTP_SELECT')}
        )
        return result


# /user/{id} route #
@app_handler.route('/user/<id_user>', methods=['DELETE'])
def user_route_delete_by_id(id_user):
    # Routing request to /user/{id} DELETE method #
    if request.method == 'DELETE':
        result = delete_user_by_id([id_user])
        return result
