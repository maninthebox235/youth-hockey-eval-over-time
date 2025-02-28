from flask import Flask
from database import init_app, db
from flask_migrate import Migrate

app = init_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000, debug=True)