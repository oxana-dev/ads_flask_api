from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, jwt


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)

    # Crear las tablas (en producción usa Flask-Migrate)
    with app.app_context():
        db.create_all()

    from app.auth.routes import auth_bp
    from app.ads.routes import ads_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ads_bp)

    @app.get("/")
    def index():
        return jsonify({
            "name": "Flask Ads API",
            "endpoints": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "list_ads": "GET /ads/",
                "get_ad": "GET /ads/<id>",
                "create_ad": "POST /ads/ (auth)",
                "update_ad": "PATCH /ads/<id> (owner)",
                "delete_ad": "DELETE /ads/<id> (owner)",
            },
        })

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(_):
        return jsonify({"error": "Unprocessable entity"}), 422

    return app