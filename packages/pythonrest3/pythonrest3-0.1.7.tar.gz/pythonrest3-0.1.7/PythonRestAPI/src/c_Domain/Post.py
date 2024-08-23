# Domain Imports #
import ujson

# Post Validator Import #
from src.e_Infra.d_Validators.a_Domain.PostValidator import *

# SqlAlchemy Import #
from src.e_Infra.b_Builders.SqlAlchemyBuilder import *


# SqlAlchemy Post domain schema #
class PostSchema(SQLAlchemySchema):
    class Meta:
        json_module = ujson
        ordered = True
        fields = ("id_post", "post", "date_time")


# SqlAlchemy Post domain class #
class Post(Base):
    __tablename__ = "post"
    id_post: str = sa.Column(sa.CHAR(36), primary_key=True, nullable=False)
    post: str = sa.Column(sa.VARCHAR(160), nullable=False)
    date_time: str = sa.Column(sa.DATETIME, nullable=False)

    def __init__(self, id_post=None, post=None, date_time=None):
        self.id_post = id_post
        self.post = post
        self.date_time = date_time

    # SqlAlchemy Post JSON schema #
    schema = PostSchema(many=True)

    # Custom Post validators #
    validate_custom_rules = validate_post
