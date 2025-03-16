from flask import Flask, jsonify
from database import init_app, db
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from utils.data_generator import seed_database
import os
import logging
from datetime import timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Set a stable secret key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-testing') #Updated SECRET_KEY setting

    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Configure login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        from database.models import User
        from utils.type_converter import to_int
        
        # Convert user_id to Python native int
        user_id = to_int(user_id)
        if user_id is None:
            return None
            
        return User.query.get(user_id)

    # Route to test email configuration
    @app.route('/test-email', methods=['GET'])
    def test_email():
        from utils.email_service import test_email_configuration
        result = test_email_configuration(mail)
        return jsonify(result)

    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    return app

def init_app():
    try:
        app = create_app()
        return app
    except Exception as e:
        logger.error(f"Failed to initialize app: {str(e)}")
        return None

if __name__ == '__main__':
    app = create_app()
    # Run Flask on port 5001 to avoid conflict with Streamlit
    app.run(host='0.0.0.0', port=5001, debug=True)