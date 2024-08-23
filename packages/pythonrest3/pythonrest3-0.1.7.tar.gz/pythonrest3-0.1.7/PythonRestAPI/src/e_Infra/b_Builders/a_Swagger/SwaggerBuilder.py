from flask_swagger_ui import get_swaggerui_blueprint
from flask import redirect, request


# Method to build Swagger Blueprint #
def build_swagger_blueprint(app_handler):

    @app_handler.route('/swagger', methods=['GET'])
    def swagger_redirect():
        return redirect('/swagger/')

    SWAGGER_URL = "/swagger"
    API_URL = "/swaggerdata"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Swagger"
        },
        blueprint_name='Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)


# Method to build Order Swagger Blueprint #
def build_order_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/order', methods=['GET'])
    def swagger_order_redirect():
        return redirect('/swagger/order/')

    SWAGGER_URL = "/swagger/order"
    API_URL = "/swaggerdata/order"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Order Swagger"
        },
        blueprint_name='Order Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)


# Method to build Post Swagger Blueprint #
def build_post_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/post', methods=['GET'])
    def swagger_post_redirect():
        return redirect('/swagger/post/')

    SWAGGER_URL = "/swagger/post"
    API_URL = "/swaggerdata/post"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Post Swagger"
        },
        blueprint_name='Post Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)


# Method to build Product Swagger Blueprint #
def build_product_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/product', methods=['GET'])
    def swagger_product_redirect():
        return redirect('/swagger/product/')

    SWAGGER_URL = "/swagger/product"
    API_URL = "/swaggerdata/product"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Product Swagger"
        },
        blueprint_name='Product Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)


# Method to build Reservation Swagger Blueprint #
def build_reservation_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/reservation', methods=['GET'])
    def swagger_reservation_redirect():
        return redirect('/swagger/reservation/')

    SWAGGER_URL = "/swagger/reservation"
    API_URL = "/swaggerdata/reservation"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Reservation Swagger"
        },
        blueprint_name='Reservation Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)


# Method to build SetTypeTable Swagger Blueprint #
def build_settypetable_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/settypetable', methods=['GET'])
    def swagger_settypetable_redirect():
        return redirect('/swagger/settypetable/')

    SWAGGER_URL = "/swagger/settypetable"
    API_URL = "/swaggerdata/settypetable"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "SetTypeTable Swagger"
        },
        blueprint_name='SetTypeTable Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)


# Method to build User Swagger Blueprint #
def build_user_swagger_blueprint(app_handler):

    @app_handler.route('/swagger/user', methods=['GET'])
    def swagger_user_redirect():
        return redirect('/swagger/user/')

    SWAGGER_URL = "/swagger/user"
    API_URL = "/swaggerdata/user"

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "User Swagger"
        },
        blueprint_name='User Swagger'
    )
    app_handler.register_blueprint(swaggerui_blueprint)
