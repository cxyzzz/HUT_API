# -*- coding=utf-8 -*-

from flask import Flask
import os


config = {
    'DEBUG': True,
    'SECRET_KEY': os.urandom(24),
    'PERMANENT_SESSION_LIFETIME': 900,
}
app = Flask(__name__)
app.config.from_mapping(config)
