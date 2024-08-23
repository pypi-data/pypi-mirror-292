# Domain Imports #
from src.c_Domain.Reservation import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves Reservation domain objects by given request_args param #
def get_reservation_set(request_args, header_args):
    return get_all(
        declarative_meta=Reservation,
        request_args=request_args,
        header_args=header_args
    )


# Method retrieves Reservation domain objects by given id and request_args params #
def get_reservation_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=Reservation,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=['id_reservation'],
        header_args=header_args
    )


# Method inserts Reservation domain objects #
def post_reservation_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=Reservation
    )


# Method updates Reservation domain objects #
def patch_reservation_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=Reservation,
        id_name_list=['id_reservation']
    )


# Method inserts and/or updates Reservation domain objects #
def put_reservation_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=Reservation,
        id_name_list=['id_reservation']
    )


# Method deletes Reservation domain object #
def delete_reservation_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=Reservation
    )


# Method deletes Reservation domain objects by given id params #
def delete_reservation_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=Reservation,
        id_value_list=id_value_list,
        id_name_list=['id_reservation']
    )
