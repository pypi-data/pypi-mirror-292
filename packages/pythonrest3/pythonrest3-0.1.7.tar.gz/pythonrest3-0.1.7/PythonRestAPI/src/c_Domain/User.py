# Domain Imports #
import ujson

# User Validator Import #
from src.e_Infra.d_Validators.a_Domain.UserValidator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy User domain schema #
class UserSchema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = ("id_user", "username", "description", "role", "date_of_creation", "date_of_birth", "date_of_last_update", "time_of_arrival", "time_of_last_update", "year_of_creation")


# SqlAlchemy User domain class #
class User(Base):
    __tablename__ = "user"
    id_user: int = sa.Column(sa.Integer, primary_key=True, nullable=False, autoincrement=True)
    username: str = sa.Column(sa.VARCHAR(30), nullable=False)
    description: str = sa.Column(sa.TEXT)
    role: str = sa.Column(sa.Enum('admin', 'manager', 'employee'))
    date_of_creation: str = sa.Column(sa.DATETIME)
    date_of_birth: str = sa.Column(sa.Date)
    date_of_last_update: str = sa.Column(sa.DATETIME)
    time_of_arrival: str = sa.Column(sa.TIME)
    time_of_last_update: str = sa.Column(sa.TIMESTAMP)
    year_of_creation: str = sa.Column(sa.String)

    def __init__(self, id_user=None, username=None, description=None, role=None, date_of_creation=None, date_of_birth=None, date_of_last_update=None, time_of_arrival=None, time_of_last_update=None, year_of_creation=None):
        self.id_user = id_user
        self.username = username
        self.description = description
        self.role = role
        self.date_of_creation = date_of_creation
        self.date_of_birth = date_of_birth
        self.date_of_last_update = date_of_last_update
        self.time_of_arrival = time_of_arrival
        self.time_of_last_update = time_of_last_update
        self.year_of_creation = year_of_creation

    # SqlAlchemy User JSON schema #
    schema = UserSchema(many=True)

    # Custom User validators #
    validate_custom_rules = validate_user
