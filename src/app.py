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
from pymssql import _mssql


class fake_mssql:
    def connect(server, user, password, database):
        return fake_mssql()

    def execute_query(self, query, params):
        return fake_mssql()

    def execute_scalar(self, query, params):
        return fake_mssql()

    def close(self):
        return fake_mssql()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = os.urandom(12)
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["DB_IP"] = os.environ.get("DB_IP")
    app.config["DB_USER"] = os.environ.get("DB_USER")
    app.config["DB_PASS"] = os.environ.get("DB_PASS")
    app.config["HTTP_USER"] = os.environ.get("HTTP_USER")
    app.config["HTTP_PASS"] = os.environ.get("HTTP_PASS")
    app.config["OPERATORS"] = os.environ.get("OPERATORS")

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    bootstrap = Bootstrap5(app)

    if app.config["DB_IP"] is None:
        dbLink = fake_mssql.connect(
            server="",
            user="",
            password="",
            database="",
        )
    else:
        dbLink = _mssql.connect(
            server=app.config["DB_IP"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASS"],
            database="wwwMaintenance",
        )

    def queryDBrow(query, params=""):
        dbLink.execute_query(query, params)
        queryResult = {}
        # trick to differentiate pymssql vs fake_mssql
        if hasattr(dbLink, "__iter__"):
            for row in dbLink:
                for column in row.keys():
                    if isinstance(column, str):
                        queryResult.update({column: row[column]})
                break
        dbLink.close
        return queryResult

    def queryDBscalar(query, params=""):
        queryResult = dbLink.execute_scalar(query, params)
        dbLink.close
        return queryResult

    @app.route("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        from src.updateuser import updateuser
        app.register_blueprint(updateuser, url_prefix="/updateuser")
        return app

    return app
