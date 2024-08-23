# Infra Imports #
from src.e_Infra.g_Environment.EnvironmentVariables import *
from src.e_Infra.b_Builders.FlaskAdminPanelBuilder import *

# Controller Imports #
from src.a_Presentation.a_Domain.UserController import *
from src.a_Presentation.a_Domain.SetTypeTableController import *
from src.a_Presentation.a_Domain.ReservationController import *
from src.a_Presentation.a_Domain.ProductController import *
from src.a_Presentation.a_Domain.PostController import *
from src.a_Presentation.a_Domain.OrderController import *
from src.a_Presentation.d_Swagger.SwaggerController import *
from src.a_Presentation.c_Redoc.RedocController import *
from src.a_Presentation.b_Custom.OptionsController import *
from src.a_Presentation.b_Custom.SQLController import *
from src.a_Presentation.b_Custom.BeforeRequestController import *
from src.a_Presentation.b_Custom.ExceptionHandlerController import *


# LocalHost run #
if __name__ == "__main__":
    app_handler.run(debug=True, use_reloader=False)
