# -*- coding=utf-8 -*-

import os
from flask import Flask
from flask_bootstrap import Bootstrap
from datetime import timedelta
from app.views import hut

config = {
    'DEBUG': True,
    'SECRET_KEY': os.urandom(24),
    'PERMANENT_SESSION_LIFETIME': timedelta(days=1),
}


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    app.config.from_mapping(config)
    app.register_blueprint(hut)
    return app
