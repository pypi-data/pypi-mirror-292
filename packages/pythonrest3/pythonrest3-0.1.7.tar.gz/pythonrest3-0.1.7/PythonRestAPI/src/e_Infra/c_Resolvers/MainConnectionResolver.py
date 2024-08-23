# Connection Imports #
from src.e_Infra.c_Resolvers.MySqlConnectionResolver import *


# Global Main Connection #
main_conn = None


# Method retrieves database connection according to selected environment #
def get_main_connection_session():

    # Assigning global variable #
    global main_conn

    if os.environ['main_db_conn'] == 'mysql':
        main_conn = get_mysql_connection_session()
        return main_conn

    return None
