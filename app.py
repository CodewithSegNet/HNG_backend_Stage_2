from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
import pymysql




app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://segun:segun@localhost/testuser'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://segun:WsC7u7CyilYxSR7R5pToOpNctCE5MOf9@dpg-cq5a63mehbks73blrrlg-a.oregon-postgres.render.com/hng_n202'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://segun:WsC7u7CyilYxSR7R5pToOpNctCE5MOf9@dpg-cq5a63mehbks73blrrlg-a/hng_n202'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config['JWT_SECRET_KEY'] = 'walkingdogs'

jwt = JWTManager(app)



# Register your blueprint with the app without prefix
from controllers.controllers import bp
app.register_blueprint(bp)

from models.users import *

from controllers.controllers import *


with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)


