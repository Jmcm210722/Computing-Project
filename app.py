"""Tiny Flask app to register API blueprints.

Usage: `python app.py` (for development). The app expects a MongoDB
instance accessible via `MONGO_URI` environment variable.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import traceback
import sys
from blueprints.workouts import workouts_bp
from blueprints.exercises import exercises_bp
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.calories import calories_bp
from routes.chatbot import chatbot_bp

# Enable logging to see errors
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)


def create_app():
    app = Flask(__name__)
    
    # Enable CORS for all routes; frontend can be on any origin
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register the workouts blueprint under the `/api/workouts` prefix
    app.register_blueprint(workouts_bp, url_prefix="/api/workouts")
    # Register the exercises blueprint under the `/api` prefix
    app.register_blueprint(exercises_bp, url_prefix="/api")
    # Register auth and profile blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    # Register calorie tracking blueprint
    app.register_blueprint(calories_bp, url_prefix="/api/calories")
    # Register chatbot blueprint
    app.register_blueprint(chatbot_bp, url_prefix="/api/chatbot")
    
    # Error handler for 500 errors to return JSON with proper CORS headers
    @app.errorhandler(500)
    def internal_error(error):
        # Log the full traceback to both logging and stderr
        error_msg = f"500 ERROR: {error}"
        tb = traceback.format_exc()
        logging.error(error_msg)
        logging.error(tb)
        print(f"\n{error_msg}\n{tb}", file=sys.stderr, flush=True)
        return jsonify({"error": "Internal server error"}), 500
    
    # Error handler for 404 errors
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
