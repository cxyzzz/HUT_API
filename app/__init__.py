# -*- coding=utf-8 -*-


import os
from flask import Flask

config = {
    'HOST': '0.0.0.0',
    'PORT': 9999,
    'DEBUG': True,
    'SECRET_KEY': os.urandom(24),
    'PERMANENT_SESSION_LIFETIME': 900,
}
app = Flask(__name__)
app.config.from_mapping(config)
from app import views
