# -*- coding: utf-8 -*-
""" main application flask

This flask app registers the blueprints such as:
updateuser ...

It picks up the shell exported variables:
'DB_IP'       ip-address-of-aladin-mssql-db
'DB_USER'     username on Aladin
'DB_PASS'     password to access Aladin
'HTTP_USER'   username for http authentication
'HTTP_PASS'   password for http authentication
'OPERATORS'   list of operator names separated by space
'API_KEY1'    API1 for post address find
'API_KEY2'    API2 for post address retrieve
'API_REFERER' referrer URL for post address APIs
'OPERATORS'   usernames separated by space
'DOMAIN'      domain name in topmenu i.e example.com

Example:
    python
    [...]

Attributes:
    [...]
"""
import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = os.urandom(12)
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["HTTP_USER"] = os.environ.get("HTTP_USER")
    app.config["HTTP_PASS"] = os.environ.get("HTTP_PASS")
    app.config["OPERATORS"] = os.environ.get("OPERATORS")
    app.config["DOMAIN"] = os.environ.get("DOMAIN")

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    bootstrap = Bootstrap5(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        from src.updateuser import updateuser
        from src.createuser import createuser
        from src.userinvoice import userinvoice
        # from src.updateinvoice import updateinvoice

        app.register_blueprint(updateuser, url_prefix="/updateuser")
        app.register_blueprint(createuser, url_prefix="/createuser")
        app.register_blueprint(userinvoice, url_prefix="/userinvoice")
        # app.register_blueprint(updareinvoice, url_prefix="/updareinvoice")
        return app

    return app
