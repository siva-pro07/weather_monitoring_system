import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Create a new SQLAlchemy object
db = SQLAlchemy()

# Create Flask app instance
def create_app():
    app = Flask(__name__)

    # Load configuration from environment variables or config file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:siva@localhost/rule_engine_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Register blueprints for routes
    from backend.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

# Entry point for running the app
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create all tables defined in models.py
        db.create_all()
    app.run(debug=True)
