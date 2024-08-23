# System Imports #
import os

# ------------------------------------------ Database ------------------------------------------ #

# Database start configuration #
os.environ['main_db_conn'] = 'mysql'

# Configuration for database connection #
os.environ['mysql_user'] = 'admin'
os.environ['mysql_password'] = 'adminuserdb'
os.environ['mysql_host'] = 'localhost'
os.environ['mysql_port'] = '3306'
os.environ['mysql_schema'] = 'userdb'


# ------------------------------------------ Domain ------------------------------------------ #

# UID Generation Type #
os.environ['id_generation_method'] = 'uuid'

# Filter generation environment variables #
os.environ['domain_like_left'] = ''
os.environ['domain_like_right'] = ''
os.environ['domain_like_full'] = ''

# Datetime valid masks #
os.environ['date_valid_masks'] = "%Y-%m-%d, %d-%m-%Y, %Y/%m/%d, %d/%m/%Y"
os.environ['time_valid_masks'] = "%H:%M:%S, %I:%M:%S %p, %H:%M, %I:%M %p, %I:%M:%S%p, %I:%M%p, %H:%M:%S%z, %I:%M:%S %p%z, %H:%M%z, %I:%M %p%z, %I:%M:%S%p%z, %I:%M%p%z, %H:%M:%S.%f, %I:%M:%S.%f %p, %H:%M:%S.%f%z, %I:%M:%S.%f %p%z, %H:%M:%S.%fZ, %I:%M:%S.%f %pZ, %H:%M:%S.%f %Z, %I:%M:%S.%f %p %Z"

os.environ['query_limit'] = '*'

# ------------------------------------------ Trace ------------------------------------------ #

# Comment this variable bellow for NO STACKTRACE (production mode off) #
os.environ['display_stacktrace_on_error'] = 'False'

# ------------------------------------------ Origins ------------------------------------------ #

# Origins enabled #
os.environ['origins'] = '*'
os.environ['headers'] = '*'
