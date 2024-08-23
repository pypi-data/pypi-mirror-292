# Domain Imports #
from src.c_Domain.Product import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves Product domain objects by given request_args param #
def get_product_set(request_args, header_args):
    return get_all(
        declarative_meta=Product,
        request_args=request_args,
        header_args=header_args
    )


# Method retrieves Product domain objects by given id and request_args params #
def get_product_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=Product,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=['id_product'],
        header_args=header_args
    )


# Method inserts Product domain objects #
def post_product_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=Product
    )


# Method updates Product domain objects #
def patch_product_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=Product,
        id_name_list=['id_product']
    )


# Method inserts and/or updates Product domain objects #
def put_product_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=Product,
        id_name_list=['id_product']
    )


# Method deletes Product domain object #
def delete_product_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=Product
    )


# Method deletes Product domain objects by given id params #
def delete_product_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=Product,
        id_value_list=id_value_list,
        id_name_list=['id_product']
    )
