from flask_cors import CORS
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

cors = CORS()
swagger = Swagger()
