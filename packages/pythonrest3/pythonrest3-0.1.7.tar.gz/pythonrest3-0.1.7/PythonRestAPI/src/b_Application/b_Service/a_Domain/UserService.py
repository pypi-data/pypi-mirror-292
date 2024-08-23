# Domain Imports #
from src.c_Domain.User import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves User domain objects by given request_args param #
def get_user_set(request_args, header_args):
    return get_all(
        declarative_meta=User,
        request_args=request_args,
        header_args=header_args
    )


# Method retrieves User domain objects by given id and request_args params #
def get_user_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=User,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=['id_user'],
        header_args=header_args
    )


# Method inserts User domain objects #
def post_user_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=User
    )


# Method updates User domain objects #
def patch_user_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=User,
        id_name_list=['id_user']
    )


# Method inserts and/or updates User domain objects #
def put_user_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=User,
        id_name_list=['id_user']
    )


# Method deletes User domain object #
def delete_user_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=User
    )


# Method deletes User domain objects by given id params #
def delete_user_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=User,
        id_value_list=id_value_list,
        id_name_list=['id_user']
    )
