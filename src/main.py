import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_restful import Api

from .models import db, ma
from .resources import BlacklistCheckResource, BlacklistResource, HealthResource

load_dotenv()


def database_uri():
    """URI de conexion: RDS PostgreSQL en AWS, SQLite local si no hay variables."""
    explicit_uri = os.getenv("DATABASE_URL")
    if explicit_uri:
        return explicit_uri

    host = os.getenv("DB_HOST")
    if not host:
        return "sqlite:///blacklist.db"

    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "blacklist")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "cambiar-en-produccion")

    db.init_app(app)
    ma.init_app(app)
    JWTManager(app)

    api = Api(app)
    api.add_resource(BlacklistResource, "/blacklists")
    api.add_resource(BlacklistCheckResource, "/blacklists/<string:email>")
    api.add_resource(HealthResource, "/health", "/")

    with app.app_context():
        db.create_all()

    @app.cli.command("generate-token")
    def generate_token():
        """Imprime el token Bearer estatico que consume la API."""
        token = create_access_token(
            identity=os.getenv("API_IDENTITY", "blacklist-service"),
            expires_delta=False,
        )
        print(token)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"message": "Recurso no encontrado."}), 404

    return app
