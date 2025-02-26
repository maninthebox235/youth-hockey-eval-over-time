from database import init_app
from flask import Flask
from flask_migrate import Migrate

app = init_app()

if __name__ == '__main__':
    with app.app_context():
        # Initialize Flask-Migrate
        migrate = Migrate(app, app.extensions['sqlalchemy'].db)
        app.run(host='0.0.0.0', port=5000, debug=True)