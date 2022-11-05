# -*- coding: utf-8 -*-
import os
from datetime import datetime as dt
from flask import Flask, render_template, request, flash, Markup, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import InputRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
from flask_sqlalchemy import SQLAlchemy
from pymssql import _mssql

class fake_mssql:
    def connect(server,user,password,database):
        return fake_mssql()
    def execute_query(self, query, params):
        return fake_mssql()
    def execute_scalar(self, query, params):
        return fake_mssql()
    def close(self):
        return fake_mssql()

"""
class DB_UserId(db.Model):
    __tablename__ = "UsersId"
    loginName = db.Column("LoginName", db.String(30), primary_key=True)
    firstName = db.Column("FirstName", db.String(30), nullable=False)
    lastName = db.Column("LastName", db.String(30), nullable=False)
    organizationName = db.Column("OrganizationName", db.String(30), nullable=True)
    address = db.Column("Address", db.String(30), nullable=True)
    city = db.Column("City", db.String(30), nullable=True)
    state = db.Column("State", db.String(30), nullable=True)
    postalCode = db.Column("PostalCode", db.String(30), nullable=True)
    country = db.Column("Country", db.String(30), nullable=True)
    homePhone = db.Column("HomePhone", db.String(30), nullable=True)
    accountNumber = db.Column("AccountNumber", db.String(30), nullable=True)
    language = db.Column("Language", db.String(30), nullable=True)
    paymentMethod = db.Column("PaymentMethod", db.String(30), nullable=True)
    creditCardNumber = db.Column("CreditCardNumber", db.String(30), nullable=True)
    creditCardExpiry = db.Column("CreditCardExpiry", db.String(30), nullable=True)
    bankName = db.Column("BankName", db.String(30), nullable=True)
    checkNumber = db.Column("CheckNumber", db.String(30), nullable=True)
    bankAccount = db.Column("BankAccount", db.String(30), nullable=True)
    identificationCard = db.Column("IdentificationCard", db.String(30), nullable=True)
    authorizationCode = db.Column("AuthorizationCode", db.String(30), nullable=True)
    operatingSystem = db.Column("OperatingSystem", db.String(30), nullable=True)
    operator = db.Column("Operator", db.String(30), nullable=True)
    referredBy = db.Column("ReferredBy", db.String(30), nullable=True)
    notes = db.Column("Notes", db.String(254), nullable=True)
    dateJoined = db.Column("DateJoined", db.String(30), nullable=True)
"""

class FormSearchLogin(FlaskForm):
    loginName = StringField(
        label="Login name",
        validators=[InputRequired(), Length(1, 20)],
        description="",
        render_kw={"placeholder": "Customer username"},
    )
    submit = SubmitField()


class FormUserDetail(FlaskForm):
    loginName = StringField(
        label="Login name",
        validators=[InputRequired(), Length(1, 20)],
        description="",
        render_kw={"placeholder": "Customer username"},
    )
    firstName = StringField(
        label="First name",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "Customer first name"},
    )
    lastName = StringField(
        label="Last name",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "Customer last name"},
    )
    submit = SubmitField()


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = "dev"
    # set bootstrap to be served locally
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB_IP = os.environ.get("DB_IP")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")

    bootstrap = Bootstrap5(app)
    db = SQLAlchemy(app)
    # csrf = CSRFProtect(app)


    if DB_IP is None:
        dbLink = fake_mssql.connect(
            server=f"{DB_IP}",
            user=f"{DB_USER}",
            password=f"{DB_PASS}",
            database="wwwMaintenance",
        )
    else:
        dbLink = _mssql.connect(
            server=f"{DB_IP}",
            user=f"{DB_USER}",
            password=f"{DB_PASS}",
            database="wwwMaintenance",
        )


    def queryDBrow(query, params=""):
        dbLink.execute_query(query, params)
        queryResult = {}
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


    def isUserExist(loginName):
        isUserExist = queryDBscalar(
            "SELECT count(*) as 'counter' from UsersId where lower(LoginName) = lower(%s)",
            loginName,
        )
        if isUserExist != 1:
            isUserExist = None
        return isUserExist


    @app.before_first_request
    def before_first_request_func():
        """
        db.drop_all()
        db.create_all()
        today = str(dt.now())
        names = {"alpha", "bravo", "charly"}
        for name in names:
            row = DB_UserId(
                loginName=f"{name}",
                firstName=f"{name} First {today[0:10]}",
                lastName=f"{name} Last {today[10:19]}",
            )
            db.session.add(row)
        db.session.commit()
        """


    @app.route("/")
    def index():
        return render_template("index.html")


    @app.route("/form", methods=["GET", "POST"])
    def test_form():
        formSearchLogin = FormSearchLogin(request.args)
        formUserDetail = FormUserDetail()
    
        if request.method == "GET" and request.args.get("LoginName") is not None:
            formSearchLogin.loginName.data = request.args.get("LoginName")
    
        if (
            "loginName" in request.args
            and formSearchLogin.validate()
            and isUserExist(formSearchLogin.data["loginName"])
        ):
            usersDict = queryDBrow(
                "SELECT FirstName, LastName from UsersId where LoginName = %s",
                formSearchLogin.data["loginName"],
            )
            """
            userInfoModel = DB_UserId()
            userInfoModel.loginName = formSearchLogin.data["loginName"]
            formUserDetail = FormUserDetail(obj=userInfoModel)
            """
            formUserDetail = FormUserDetail()
            formUserDetail.firstName.data = usersDict["FirstName"]
            formUserDetail.lastName.data = usersDict["LastName"]

        if formUserDetail.validate_on_submit():
            try:
                """
                formUserDetail.populate_obj(userInfoModel)
                db.session.add(userInfoModel)
                db.session.commit()
                """
                flash('LoginName="' + formUserDetail.data["loginName"] + '"', "success")
                # return redirect(url_for('test_form'))
                return render_template(
                    "form.html",
                    formSearchLogin=formSearchLogin,
                    formUserDetail=formUserDetail,
                )
            except:
                # db.session.rollback()
                flash("Error: could not save.", "danger")

        return render_template(
            "form.html", formSearchLogin=formSearchLogin, formUserDetail=formUserDetail
        )

    return app


# if __name__ == "__main__":
#    app.run(debug=True)
