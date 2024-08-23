# Domain Imports #
import ujson

# Product Validator Import #
from src.e_Infra.d_Validators.a_Domain.ProductValidator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy Product domain schema #
class ProductSchema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = ("id_product", "name", "category")


# SqlAlchemy Product domain class #
class Product(Base):
    __tablename__ = "product"
    id_product: str = sa.Column(sa.CHAR(36), primary_key=True, nullable=False)
    name: str = sa.Column(sa.VARCHAR(100), nullable=False)
    category: str = sa.Column(SET('electronics', 'clothing', 'books', 'home_decor'), nullable=False)

    def __init__(self, id_product=None, name=None, category=None):
        self.id_product = id_product
        self.name = name
        self.category = category

    # SqlAlchemy Product JSON schema #
    schema = ProductSchema(many=True)

    # Custom Product validators #
    validate_custom_rules = validate_product
