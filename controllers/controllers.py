from flask import jsonify, request, Blueprint
from controllers import db, User
from models.users import validate_fields
import json


# Create a Blueprint for your controllers
bp = Blueprint('controllers', __name__)

@bp.route('/registration', methods=['POST'])
def registration():
    """
    User's registration route
    """
    data = request.get_json()

    # validate the user data
    errors = validate_fields(data)
    if errors:
        return jsonify({"errors": errors}), 422

    try:
        new_user = User(
            userId=data['userId'],
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            password=data['password'],
            phone=data['phone']
        )
        # Hash the password
        new_user.set_password(new_user.password)

        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User Created Successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@bp.route('/login', methods=['POST'])
def login():