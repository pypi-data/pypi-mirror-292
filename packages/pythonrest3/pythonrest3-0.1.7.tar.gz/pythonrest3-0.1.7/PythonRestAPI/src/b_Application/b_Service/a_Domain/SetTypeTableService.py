# Domain Imports #
from src.c_Domain.SetTypeTable import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves SetTypeTable domain objects by given request_args param #
def get_set_type_table_set(request_args, header_args):
    return get_all(
        declarative_meta=SetTypeTable,
        request_args=request_args,
        header_args=header_args
    )


# Method retrieves SetTypeTable domain objects by given id and request_args params #
def get_set_type_table_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=SetTypeTable,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=['id_set_type_table'],
        header_args=header_args
    )


# Method inserts SetTypeTable domain objects #
def post_set_type_table_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=SetTypeTable
    )


# Method updates SetTypeTable domain objects #
def patch_set_type_table_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=SetTypeTable,
        id_name_list=['id_set_type_table']
    )


# Method inserts and/or updates SetTypeTable domain objects #
def put_set_type_table_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=SetTypeTable,
        id_name_list=['id_set_type_table']
    )


# Method deletes SetTypeTable domain object #
def delete_set_type_table_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=SetTypeTable
    )


# Method deletes SetTypeTable domain objects by given id params #
def delete_set_type_table_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=SetTypeTable,
        id_value_list=id_value_list,
        id_name_list=['id_set_type_table']
    )
