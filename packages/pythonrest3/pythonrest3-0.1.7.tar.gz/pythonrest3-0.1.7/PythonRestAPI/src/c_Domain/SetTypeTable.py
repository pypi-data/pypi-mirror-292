# Domain Imports #
import ujson

# SetTypeTable Validator Import #
from src.e_Infra.d_Validators.a_Domain.SetTypeTableValidator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy SetTypeTable domain schema #
class SetTypeTableSchema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = ("id_set_type_table", "text_col", "enum_col", "set_col")


# SqlAlchemy SetTypeTable domain class #
class SetTypeTable(Base):
    __tablename__ = "set_type_table"
    id_set_type_table: str = sa.Column(sa.CHAR(36), primary_key=True, nullable=False)
    text_col: str = sa.Column(sa.TEXT)
    enum_col: str = sa.Column(sa.Enum('enum1', 'enum2'), server_default=sa.FetchedValue())
    set_col: str = sa.Column(SET('set1', 'set2'), server_default=sa.FetchedValue())

    def __init__(self, id_set_type_table=None, text_col=None, enum_col=None, set_col=None):
        self.id_set_type_table = id_set_type_table
        self.text_col = text_col
        self.enum_col = enum_col
        self.set_col = set_col

    # SqlAlchemy SetTypeTable JSON schema #
    schema = SetTypeTableSchema(many=True)

    # Custom SetTypeTable validators #
    validate_custom_rules = validate_set_type_table
