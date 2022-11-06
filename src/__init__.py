# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, flash, Markup, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import InputRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
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
    firstName = StringField(
        label="firstName",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "firstName"},
    )
    lastName = StringField(
        label="lastName",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "lastName"},
    )
    organizationName = StringField(
        label="organizationName",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "organizationName"},
    )
    address = StringField(
        label="address",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "address"},
    )
    city = StringField(
        label="city",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "city"},
    )
    state = StringField(
        label="state",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "state"},
    )
    postalCode = StringField(
        label="postalCode",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "postalCode"},
    )
    country = StringField(
        label="country",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "country"},
    )
    homePhone = StringField(
        label="homePhone",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "homePhone"},
    )
    accountNumber = StringField(
        label="accountNumber",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "accountNumber"},
    )
    language = StringField(
        label="language",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "language"},
    )
    paymentMethod = StringField(
        label="paymentMethod",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "paymentMethod"},
    )
    creditCardNumber = StringField(
        label="creditCardNumber",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "creditCardNumber"},
    )
    creditCardExpiry = StringField(
        label="creditCardExpiry",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "creditCardExpiry"},
    )
    bankName = StringField(
        label="bankName",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "bankName"},
    )
    checkNumber = StringField(
        label="checkNumber",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "checkNumber"},
    )
    bankAccount = StringField(
        label="bankAccount",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "bankAccount"},
    )
    identificationCard = StringField(
        label="identificationCard",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "identificationCard"},
    )
    authorizationCode = StringField(
        label="authorizationCode",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "authorizationCode"},
    )
    operatingSystem = StringField(
        label="operatingSystem",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "operatingSystem"},
    )
    operator = StringField(
        label="operator",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "operator"},
    )
    referredBy = StringField(
        label="referredBy",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "referredBy"},
    )
    notes = StringField(
        label="notes",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "notes"},
    )
    dateJoined = StringField(
        label="dateJoined",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "dateJoined"},
    )
    submit = SubmitField()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        BOOTSTRAP_SERVE_LOCAL=True,
        WTF_CSRF_ENABLED=False,
    )
    app.config["DB_IP"] = os.environ.get("DB_IP")
    app.config["DB_USER"] = os.environ.get("DB_USER")
    app.config["DB_PASS"] = os.environ.get("DB_PASS")
    # DB_IP = os.environ.get("DB_IP")
    # DB_USER = os.environ.get("DB_USER")
    # DB_PASS = os.environ.get("DB_PASS")

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
                """SELECT
                  FirstName,
                  LastName,
                  OrganizationName,
                  Address,
                  City,
                  State,
                  PostalCode,
                  Country,
                  HomePhone,
                  AccountNumber,
                  Language,
                  PaymentMethod,
                  CreditCardNumber,
                  CreditCardExpiry,
                  BankName,
                  CheckNumber,
                  BankAccount,
                  IdentificationCard,
                  AuthorizationCode,
                  OperatingSystem,
                  Operator,
                  ReferredBy,
                  Notes,
                  DateJoined
                FROM
                  UsersId
                WHERE
                  LoginName = %s
                """,
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
            formUserDetail.organizationName.data = usersDict["OrganizationName"]
            formUserDetail.address.data = usersDict["Address"]
            formUserDetail.city.data = usersDict["City"]
            formUserDetail.state.data = usersDict["State"]
            formUserDetail.postalCode.data = usersDict["PostalCode"]
            formUserDetail.country.data = usersDict["Country"]
            formUserDetail.homePhone.data = usersDict["HomePhone"]
            formUserDetail.accountNumber.data = usersDict["AccountNumber"]
            formUserDetail.language.data = usersDict["Language"]
            formUserDetail.paymentMethod.data = usersDict["PaymentMethod"]
            formUserDetail.creditCardNumber.data = usersDict["CreditCardNumber"]
            formUserDetail.creditCardExpiry.data = usersDict["CreditCardExpiry"]
            formUserDetail.bankName.data = usersDict["BankName"]
            formUserDetail.checkNumber.data = usersDict["CheckNumber"]
            formUserDetail.bankAccount.data = usersDict["BankAccount"]
            formUserDetail.identificationCard.data = usersDict["IdentificationCard"]
            formUserDetail.authorizationCode.data = usersDict["AuthorizationCode"]
            formUserDetail.operatingSystem.data = usersDict["OperatingSystem"]
            formUserDetail.operator.data = usersDict["Operator"]
            formUserDetail.referredBy.data = usersDict["ReferredBy"]
            formUserDetail.notes.data = usersDict["Notes"]
            formUserDetail.dateJoined.data = usersDict["DateJoined"]

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
