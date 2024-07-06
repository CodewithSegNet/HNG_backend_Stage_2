from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://segun:segun@localhost/testuser'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)


# Register your blueprint with the app without prefix
from controllers.controllers import bp
app.register_blueprint(bp)

from models.users import *

from controllers.controllers import *


with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)


