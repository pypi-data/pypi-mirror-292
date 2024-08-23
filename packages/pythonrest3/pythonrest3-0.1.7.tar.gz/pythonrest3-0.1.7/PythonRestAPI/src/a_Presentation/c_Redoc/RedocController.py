from src.e_Infra.b_Builders.FlaskBuilder import *


# Methods to create main Redoc docs #
@redoc_blueprint.route('/redoc')
def redoc():
    return render_template('redoc.html')


@redoc_blueprint.route('/redoc/spec')
def spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'swagger.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Methods to build Order Redoc docs #
@redoc_blueprint.route('/redoc/order')
def order_redoc():
    return render_template('Order.html')


@redoc_blueprint.route('/redoc/spec/order')
def order_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'Order.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Methods to build Post Redoc docs #
@redoc_blueprint.route('/redoc/post')
def post_redoc():
    return render_template('Post.html')


@redoc_blueprint.route('/redoc/spec/post')
def post_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'Post.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Methods to build Product Redoc docs #
@redoc_blueprint.route('/redoc/product')
def product_redoc():
    return render_template('Product.html')


@redoc_blueprint.route('/redoc/spec/product')
def product_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'Product.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Methods to build Reservation Redoc docs #
@redoc_blueprint.route('/redoc/reservation')
def reservation_redoc():
    return render_template('Reservation.html')


@redoc_blueprint.route('/redoc/spec/reservation')
def reservation_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'Reservation.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Methods to build SetTypeTable Redoc docs #
@redoc_blueprint.route('/redoc/settypetable')
def settypetable_redoc():
    return render_template('SetTypeTable.html')


@redoc_blueprint.route('/redoc/spec/settypetable')
def settypetable_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'SetTypeTable.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Methods to build User Redoc docs #
@redoc_blueprint.route('/redoc/user')
def user_redoc():
    return render_template('User.html')


@redoc_blueprint.route('/redoc/spec/user')
def user_spec():
    yaml_path = os.path.join(os.getcwd(), 'config', 'User.yaml')
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    return yaml_content


# Register the blueprint
app_handler.register_blueprint(redoc_blueprint)
