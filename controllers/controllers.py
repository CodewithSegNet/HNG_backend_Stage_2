from flask import current_app, jsonify, request, Blueprint, abort
from controllers import db, User, Organisation
from models.users import validate_fields
from app import JWTManager, jwt_required, get_jwt_identity, create_access_token
import jwt
from datetime import datetime, timedelta
import json
import logging



# Create a Blueprint for your controllers
bp = Blueprint('controllers', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@bp.route('/auth/register', methods=['POST'])
def registration():
    """
    User's registration route
    """
    data = request.get_json()

    # Logging the incoming data for debugging
    logging.debug(f"Registration request data: {data}")

    # validate the user data
    errors = validate_fields(data)
    if errors:
        return jsonify({"errors": errors}), 422
        
        
    try:
        # Create organisation
        organisation_name = f"{data['firstName']}'s organisation"
        new_organisation = Organisation(
            name=organisation_name,
            description=f"{organisation_name}'s default description"
        )
        db.session.add(new_organisation)
        db.session.flush()


        # create user
        new_user = User(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            password=data['password'],
            phone=data['phone'],
            organisation_id=new_organisation.orgId
        )
        # Hash the password
        new_user.set_password(data['password'])

        # Add the user to the session but don't commit yet
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.userId)


        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": new_user.userId,
                    "firstName": new_user.firstName,
                    "lastName": new_user.lastName,
                    "email": new_user.email,
                    "phone": new_user.phone
                }
            }
        }), 201
    except Exception as e:
        logging.error(f"Registration failed: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "Bad request", "message": "Registration unsuccessful", "statusCode": 400}), 400
        




# Login route

@bp.route('/auth/login', methods=['POST'])
def login():
    """
    login route for registered user 
    """
    try:
        email=request.json.get('email')
        password=request.json.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            token = create_access_token(identity=user.userId, expires_delta=timedelta(hours=2))

            # Retrieve organisation details
            organisation = Organisation.query.filter_by(orgId=user.organisation_id).first()
            organisation_data = {
                "orgId": organisation.orgId,
                "name": organisation.name,
                "description": organisation.description
            } if organisation else None

            return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone
                }
            }
        }), 201
        else:
            return jsonify({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}), 400
    except Exception as e:
        return jsonify({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}), 400





@bp.route('/api/users/<userId>', methods=['GET'])
@jwt_required()
def get_user(userId):
    current_user_id = get_jwt_identity()

    # Check if the requested user ID matches the authenticated user's ID
    if userId != current_user_id:
        return jsonify({"msg": "Unauthorized access"}), 403

    try:
        user = User.query.filter_by(userId=userId).first()

        if not user:
            return jsonify({"msg": f"User with ID {userId} not found"}), 404

        # Fetch organisations the user belongs to
        organisations = Organisation.query.filter(Organisation.users.any(userId=userId)).all()

        # Prepare response payload
        user_data = {
            "userId": user.userId,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone": user.phone
        }

        # Message based on the context of the request
        message = "User record retrieved successfully"

        return jsonify({
            "status": "success",
            "message": message,
            "data": user_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle JWT errors
@bp.errorhandler
def handle_jwt_errors(e):
    if isinstance(e, JWTError):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    return jsonify({"error": str(e)}), 500



@bp.route('/api/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    try:
        current_user_id = get_jwt_identity()

        # Query organisations where current user's ID is in the users relationship
        organisations = Organisation.query.filter(Organisation.users.any(User.userId == current_user_id)).all()

        if not organisations:
            return jsonify({"status": "error", "message": "Organisations not found", "statusCode": 404}), 404

        organisations_data = [{
            "orgId": org.orgId,
            "name": org.name,
            "description": org.description
        } for org in organisations]

        return jsonify({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": organisations_data
        }), 200
    except Exception as e:
        logging.error(f"Failed to fetch organisations: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to fetch organisations", "statusCode": 500}), 500





@bp.route('/api/organisations/<orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    try:
        current_user_id = get_jwt_identity()

        # Query the organisation based on orgId and user's identity
        organisation = Organisation.query.filter_by(orgId=orgId).first()

        # Check if organisation exists and if the current user has access
        if not organisation or current_user_id not in [user.userId for user in organisation.users]:
            abort(404, description=f"Organisation with ID {orgId} not found or you do not have access")


        # Prepare response payload
        org_data = {
            "orgId": organisation.orgId,
            "name": organisation.name,
            "description": organisation.description
        }

        return jsonify({
            "status": "success",
            "message": "Organisation record retrieved successfully",
            "data": org_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@bp.route('/api/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate request body
        if 'name' not in data or not data['name']:
            return jsonify({"error": "Name is required"}), 400

        # Create new organisation with current_user_id
        new_organisation = Organisation(
            name=data['name'],
            description=data.get('description')
        )

        # Add current user to the organisation
        current_user = User.query.get(current_user_id)
        new_organisation.users.append(current_user)

        # Add to database session and commit
        db.session.add(new_organisation)
        db.session.commit()

        # Prepare response payload
        org_data = {
            "orgId": new_organisation.orgId,
            "name": new_organisation.name,
            "description": new_organisation.description
        }

        return jsonify({
            "status": "success",
            "message": "Organisation created successfully",
            "data": org_data
        }), 201

    except Exception as e:
        logging.error(f"Failed to create organisation: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": "Failed to create organisation", "statusCode": 500}), 500




@bp.route('/api/organisations/<orgId>/users', methods=['POST'])
def add_user_to_organisation(orgId):
    data = request.get_json()
    user_id = data.get('userId')

    organisation = Organisation.query.filter_by(orgId=orgId).first()
    if not organisation:
        abort(404, description=f"Organization with ID {orgId} not found")

    user = User.query.get(user_id)
    if not user:
        abort(404, description=f"User with ID {user_id} not found")

    if user.organisation_id != orgId:
        user.organisation_id = orgId
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "User added to organisation successfully"
        }), 200
    else:
        return jsonify({
            "status": "success",
            "message": "User added to organisation successfully"
        }), 200