# Infra Imports #
from src.e_Infra.CustomVariables import *


# Method validates Post domain attributes from a Post API request item #
def validate_post(post_item):
    # Defining error list to be returned #
    error_list = get_system_empty_list()

    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # --- Define your validations here --- #
    # return error list if vot valid #
    if error_list == get_system_empty_list():
        return None
    else:
        raise Exception(error_list)
