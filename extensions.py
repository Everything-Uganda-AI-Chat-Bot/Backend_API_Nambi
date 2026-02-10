from flask_cors import CORS
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

cors = CORS()
swagger = Swagger()
