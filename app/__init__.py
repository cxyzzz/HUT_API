# -*- coding=utf-8 -*-

from flask import Flask
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 900
