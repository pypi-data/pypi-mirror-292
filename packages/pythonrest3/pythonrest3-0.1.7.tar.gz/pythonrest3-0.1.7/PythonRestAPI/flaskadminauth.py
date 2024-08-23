from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    # Perform authentication and return a JWT token if successful
    access_token = create_access_token(identity='your-identity')
    return jsonify(access_token=access_token)

# Example protected route
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
	
	
###################################################################################
from flask_admin import Admin, AdminIndexView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import redirect, url_for

class MyAdminIndexView(AdminIndexView):

    @jwt_required()
    def is_accessible(self):
        # Implement your logic to check if the current user has access
        # This could involve checking the user's role or permissions
        current_user = get_jwt_identity()
        return current_user == 'admin'  # Adjust this logic as needed

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if the user doesn't have access
        return redirect(url_for('login'))

# Initialize the Flask-Admin extension
admin = Admin(app, index_view=MyAdminIndexView())

###################################################################################

from flask_admin.contrib.sqla import ModelView

class MyModelView(ModelView):

    @jwt_required()
    def is_accessible(self):
        current_user = get_jwt_identity()
        return current_user == 'admin'  # Adjust logic as per your requirements

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
		
admin.add_view(MyModelView(YourModel, db.session))