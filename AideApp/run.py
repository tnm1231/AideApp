# from app import create_app
from flask import Flask
from app.models.models import db
from app.routes import routes_blueprint
from flask_migrate import Migrate

# app = create_app()
# app = Flask(__name__)
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aide_checks.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aide_checks.db'  

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# with app.app_context():
#     db.create_all()
migrate = Migrate(app, db)
app.register_blueprint(routes_blueprint)


if __name__ == "__main__":
    app.run(debug=True)
    print(app.config['SQLALCHEMY_DATABASE_URI'])
