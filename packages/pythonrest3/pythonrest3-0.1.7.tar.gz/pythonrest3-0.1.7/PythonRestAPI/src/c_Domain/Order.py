# Domain Imports #
import ujson

# Order Validator Import #
from src.e_Infra.d_Validators.a_Domain.OrderValidator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy Order domain schema #
class OrderSchema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = ("id_order", "order_number", "order_status", "category")


# SqlAlchemy Order domain class #
class Order(Base):
    __tablename__ = "order"
    id_order: str = sa.Column(sa.CHAR(36), primary_key=True, nullable=False)
    order_number: str = sa.Column(sa.VARCHAR(20), nullable=False)
    order_status: str = sa.Column(sa.Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
    category: str = sa.Column(SET('furniture', 'electronics', 'clothing', 'books'))

    def __init__(self, id_order=None, order_number=None, order_status=None, category=None):
        self.id_order = id_order
        self.order_number = order_number
        self.order_status = order_status
        self.category = category

    # SqlAlchemy Order JSON schema #
    schema = OrderSchema(many=True)

    # Custom Order validators #
    validate_custom_rules = validate_order
