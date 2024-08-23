from src.e_Infra.b_Builders.FlaskBuilder import app_handler
from flask_admin import Admin
from src.c_Domain.a_FlaskAdminPanel.FlaskAdminModelViews import *
from src.e_Infra.c_Resolvers.MySqlConnectionResolver import get_mysql_connection_session
from src.c_Domain.Order import Order
from src.c_Domain.Post import Post
from src.c_Domain.Product import Product
from src.c_Domain.Reservation import Reservation
from src.c_Domain.SetTypeTable import SetTypeTable
from src.c_Domain.User import User


admin = Admin(app_handler)
app_handler.secret_key = '1234'

admin.add_view(OrderModelView(Order, get_mysql_connection_session()))
admin.add_view(PostModelView(Post, get_mysql_connection_session()))
admin.add_view(ProductModelView(Product, get_mysql_connection_session()))
admin.add_view(ReservationModelView(Reservation, get_mysql_connection_session()))
admin.add_view(SetTypeTableModelView(SetTypeTable, get_mysql_connection_session()))
admin.add_view(UserModelView(User, get_mysql_connection_session()))

