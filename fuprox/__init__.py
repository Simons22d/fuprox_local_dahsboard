from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from decouple import config
from dotenv import load_dotenv
import os

load_dotenv()

# home directory
from pathlib import Path

home = str(Path.home())
current_dir = os.getcwd()

# making the directory for the files
os.chdir(home)

# mkdir
# check if home dir exists
if not os.path.exists(f"{home}/noqueue/uploads"):
    try:
        upload_path = os.path.join(home, "noqueue", "uploads")
        new_dir = Path(upload_path)
        new_dir.mkdir(parents=True)
    except OSError:
        logging.info("error Creating dir")

# move back to the current working DIR
os.chdir(current_dir)

# adding JWT other app


db_pass = os.getenv('DBPASS')
db_user = os.getenv("DBUSER")
db_host = os.getenv("DBHOST")
db = os.getenv("DB")

app = Flask(__name__)
app.config["SECRET_KEY"] = '2345'
# basedir  = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:3306/{db}"
# app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_pass}@localhost:5432/fuprox"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = f"{home}/noqueue/uploads"

try:
    db = SQLAlchemy(app)
except sqlalchemy.exc.ProgrammingError as e:
    print("error", e)

ma = Marshmallow(app)

# init bcrypt
bcrypt = Bcrypt(app)

# init the login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# setting the config options for mail
app.config["MAIL_USERNAME"] = "denniskiruku@gmail.com"
app.config["MAIL_PASSWORD"] = "*****"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_PORT"] = 587

mail = Mail()

from fuprox import routes
