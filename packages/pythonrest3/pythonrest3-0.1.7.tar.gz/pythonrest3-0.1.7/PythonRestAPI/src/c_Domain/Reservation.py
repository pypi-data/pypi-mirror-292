# Domain Imports #
import ujson

# Reservation Validator Import #
from src.e_Infra.d_Validators.a_Domain.ReservationValidator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy Reservation domain schema #
class ReservationSchema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = ("id_reservation", "guest_name", "reservation_status", "reservation_category")


# SqlAlchemy Reservation domain class #
class Reservation(Base):
    __tablename__ = "reservation"
    id_reservation: str = sa.Column(sa.CHAR(36), primary_key=True, nullable=False)
    guest_name: str = sa.Column(sa.VARCHAR(100), nullable=False)
    reservation_status: str = sa.Column(sa.Enum('reserved', 'checked_in', 'checked_out', 'cancelled'), nullable=False)
    reservation_category: str = sa.Column(SET('standard_room', 'suite', 'conference_room', 'spa_service'), nullable=False)

    def __init__(self, id_reservation=None, guest_name=None, reservation_status=None, reservation_category=None):
        self.id_reservation = id_reservation
        self.guest_name = guest_name
        self.reservation_status = reservation_status
        self.reservation_category = reservation_category

    # SqlAlchemy Reservation JSON schema #
    schema = ReservationSchema(many=True)

    # Custom Reservation validators #
    validate_custom_rules = validate_reservation
