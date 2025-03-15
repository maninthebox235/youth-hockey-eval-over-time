from flask import Flask
from database import init_app, db
from flask_migrate import Migrate
from flask_mail import Mail
from utils.data_generator import seed_database
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Configure Flask app
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure Flask-Mail with Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    app.config['MAIL_MAX_EMAILS'] = 5  # Limit of emails to send in a single connection
    app.config['MAIL_DEBUG'] = True  # Enable debug mode for troubleshooting
    
    # Log mail configuration (without sensitive data)
    logger.info(f"Mail server: {app.config['MAIL_SERVER']}")
    logger.info(f"Mail port: {app.config['MAIL_PORT']}")
    logger.info(f"Mail use TLS: {app.config['MAIL_USE_TLS']}")
    logger.info(f"Mail username configured: {'Yes' if app.config['MAIL_USERNAME'] else 'No'}")
    logger.info(f"Mail password configured: {'Yes' if app.config['MAIL_PASSWORD'] else 'No'}")
    logger.info(f"Mail default sender configured: {'Yes' if app.config['MAIL_DEFAULT_SENDER'] else 'No'}")

    # Initialize Flask-Mail
    mail = Mail(app)

    # Initialize database
    db.init_app(app)

    return app, mail

# Initialize Flask app and extensions
app, mail = create_app()
migrate = Migrate(app, db)

# Route to test email configuration
@app.route('/test-email', methods=['GET'])
def test_email():
    from utils.email_service import test_email_configuration
    from flask import jsonify
    
    result = test_email_configuration(mail)
    return jsonify(result)

if __name__ == '__main__':
    try:
        # Create all tables before running migrations
        with app.app_context():
            db.create_all()

            # Check if database needs seeding
            from database.models import Player
            if not Player.query.first():
                print("No players found, seeding database...")
                if seed_database(n_players=20):
                    print("Database seeded successfully")
                else:
                    print("Error seeding database")
            else:
                print("Database already contains data")

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

    # Run Flask on port 5001 to avoid conflict with Streamlit
    app.run(host='0.0.0.0', port=5001, debug=True)