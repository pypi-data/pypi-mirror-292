# Infra Imports #
from src.e_Infra.CustomVariables import *


# Method validates SetTypeTable domain attributes from a SetTypeTable API request item #
def validate_set_type_table(set_type_table_item):
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
