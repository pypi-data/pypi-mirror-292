# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.a_Domain.ReservationService import *

# Decorator Imports #
from src.e_Infra.f_Decorators.JsonLoadsDecorator import *


# /reservation route #
@app_handler.route('/reservation', methods=['GET'])
def reservation_route_get():
    # Routing request to /reservation GET method #
    if request.method == 'GET':
        result = get_reservation_set(
            request.args.to_dict(), {'HTTP_SELECT': request.environ.get('HTTP_SELECT'),
                                     'HTTP_ORDERBY': request.environ.get('HTTP_ORDERBY'),
                                     'HTTP_LIMIT': request.environ.get('HTTP_LIMIT'),
                                     'HTTP_PAGE': request.environ.get('HTTP_PAGE')}
        )
        return result


# /reservation route #
@app_handler.route('/reservation', methods=['POST', 'PATCH', 'PUT'])
def reservation_route_post_patch_put():
    # Routing request to /reservation POST method #
    if request.method == 'POST':
        result = post_reservation_set(request.json)
        return result
    # Routing request to /reservation PATCH method #
    if request.method == 'PATCH':
        result = patch_reservation_set(request.json)
        return result
    if request.method == 'PUT':
        result = put_reservation_set(request.json)
        return result


# /reservation route #
@app_handler.route('/reservation', methods=['DELETE'])
def reservation_route_delete_by_full_match():
    # Routing request to /reservation DELETE method #
    if request.method == 'DELETE':
        result = delete_reservation_by_full_match(request.json)
        return result


# /reservation/{id} route #
@app_handler.route('/reservation/<id_reservation>', methods=['GET'])
def reservation_route_get_by_id(id_reservation):
    # Routing request to /reservation/{id} GET method #
    if request.method == 'GET':
        result = get_reservation_by_id(
            [id_reservation], request.args.to_dict(
            ), {'HTTP_SELECT': request.environ.get('HTTP_SELECT')}
        )
        return result


# /reservation/{id} route #
@app_handler.route('/reservation/<id_reservation>', methods=['DELETE'])
def reservation_route_delete_by_id(id_reservation):
    # Routing request to /reservation/{id} DELETE method #
    if request.method == 'DELETE':
        result = delete_reservation_by_id([id_reservation])
        return result
