import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis

db = SQLAlchemy()
cache = None

def create_app(test_config=None):
    global cache

    app = Flask(__name__)

    if test_config is None:
        POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
        POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
        POSTGRES_DB = os.getenv('POSTGRES_DB', 'mydatabase')
        POSTGRES_HOST = os.getenv('DB_HOST', 'db')
        POSTGRES_PORT = os.getenv('DB_PORT', 5432)

        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
        REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    else:
        app.config.update(test_config)
        cache = None

    db.init_app(app)

    class User(db.Model):
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)

    with app.app_context():
        db.create_all()

    @app.route('/users')
    def get_users():
        if cache:
            cached = cache.get('users')
            if cached:
                return jsonify(eval(cached.decode('utf-8')))
        users = User.query.all()
        users_list = [{"id": u.id, "name": u.name} for u in users]
        if cache:
            cache.setex('users', 60, str(users_list))
        return jsonify(users_list)

    app.db = db
    app.User = User

    return app

