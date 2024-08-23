# Domain Imports #
from src.c_Domain.Post import *

# Repository Imports #
from src.d_Repository.GenericRepository import *


# Method retrieves Post domain objects by given request_args param #
def get_post_set(request_args, header_args):
    return get_all(
        declarative_meta=Post,
        request_args=request_args,
        header_args=header_args
    )


# Method retrieves Post domain objects by given id and request_args params #
def get_post_by_id(id_value_list, request_args, header_args):
    return get_by_id(
        declarative_meta=Post,
        id_value_list=id_value_list,
        request_args=request_args,
        id_name_list=['id_post'],
        header_args=header_args
    )


# Method inserts Post domain objects #
def post_post_set(request_data):
    return insert_object_set(
        request_data=request_data,
        declarative_meta=Post
    )


# Method updates Post domain objects #
def patch_post_set(request_data):
    return update_object_set(
        request_data=request_data,
        declarative_meta=Post,
        id_name_list=['id_post']
    )


# Method inserts and/or updates Post domain objects #
def put_post_set(request_data):
    return put_object_set(
        request_data=request_data,
        declarative_meta=Post,
        id_name_list=['id_post']
    )


# Method deletes Post domain object #
def delete_post_by_full_match(request_data):
    return delete_set_by_full_match(
        request_data=request_data,
        declarative_meta=Post
    )


# Method deletes Post domain objects by given id params #
def delete_post_by_id(id_value_list):
    return delete_by_id(
        declarative_meta=Post,
        id_value_list=id_value_list,
        id_name_list=['id_post']
    )
