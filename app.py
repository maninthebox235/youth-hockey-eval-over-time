from database import init_app
from flask import Flask
from flask_migrate import Migrate

app = init_app()

if __name__ == '__main__':
    with app.app_context():
        app.run(host='0.0.0.0', port=5000, debug=True)