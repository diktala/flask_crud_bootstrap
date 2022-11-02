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

dbLink = _mssql.connect(
    server=f"{DB_IP}",
    user=f"{DB_USER}",
    password=f"{DB_PASS}",
    database="wwwMaintenance",
)


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


@app.before_first_request
def before_first_request_func():
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/form", methods=["GET", "POST"])
def test_form():
    formSearchLogin = FormSearchLogin(request.args)
    formUserDetail = FormUserDetail()

    if request.method == "GET" and request.args.get("LoginName") is not None:
        formSearchLogin.loginName.data = request.args.get("LoginName")

    if "loginName" in request.args and formSearchLogin.validate():
        # using sqlalchemy
        exampleUser = db.session.execute(
            db.select(DB_UserId).where(
                DB_UserId.loginName == formSearchLogin.data["loginName"]
            )
        ).scalar()
        formUserDetail = FormUserDetail(obj=exampleUser)

        # using pure pymssql
        dbLink.execute_query("SELECT * from taxes")
        for row in dbLink:
            print(f"TaxCode: {row['TaxCode']} -- Tax1: {row['Tax1']}")
        print(f"Rows affected: {dbLink.rows_affected}")
        dbLink.close

        # using pure pymssql
        isUserExist = dbLink.execute_scalar(
            "SELECT count(*) as 'counter' from UsersId where lower(LoginName) = lower(%s)",
            formSearchLogin.data["loginName"],
        )
        print(f"isUserExist: {isUserExist}")
        dbLink.close

    if formUserDetail.validate_on_submit():
        try:
            formUserDetail.populate_obj(exampleUser)
            db.session.add(exampleUser)
            db.session.commit()
            flash('LoginName="' + formUserDetail.data["loginName"] + '"', "success")
            # return redirect(url_for('test_form'))
            return render_template(
                "form.html",
                formSearchLogin=formSearchLogin,
                formUserDetail=formUserDetail,
            )
        except:
            db.session.rollback()
            flash("Error: could not save.", "danger")

    return render_template(
        "form.html", formSearchLogin=formSearchLogin, formUserDetail=formUserDetail
    )


if __name__ == "__main__":
    app.run(debug=True)
