# Domain Imports #
from src.c_Domain.Order import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves Order domain objects by given request_args param #
def get_order_set(request_args, header_args):
    return get_all(
        declarative_meta=Order,
        request_args=request_args,
        header_args=header_args
    )


# Method retrieves Order domain objects by given id and request_args params #
def get_order_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=Order,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=['id_order'],
        header_args=header_args
    )


# Method inserts Order domain objects #
def post_order_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=Order
    )


# Method updates Order domain objects #
def patch_order_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=Order,
        id_name_list=['id_order']
    )


# Method inserts and/or updates Order domain objects #
def put_order_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=Order,
        id_name_list=['id_order']
    )


# Method deletes Order domain object #
def delete_order_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=Order
    )


# Method deletes Order domain objects by given id params #
def delete_order_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=Order,
        id_value_list=id_value_list,
        id_name_list=['id_order']
    )
