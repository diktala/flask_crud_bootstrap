# -*- coding: utf-8 -*-
import os
import re
from flask import Flask, render_template, request, flash, Markup, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import InputRequired, Optional, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
from pymssql import _mssql
from werkzeug.middleware.proxy_fix import ProxyFix
from src.canadapost import getIDsFromIndex, getIndexFromPostal, getAddressFromID


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
        validators=[
            InputRequired(),
            Regexp(
                "^[a-z_.-]+$", flags=re.IGNORECASE, message="incorrect characters used"
            ),
            Length(1, 20),
        ],
        description="",
        render_kw={"placeholder": "Customer username"},
    )
    submit = SubmitField(label="Search")


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
    lookupAddress = SubmitField(label="Lookup")
    addressSelect = SelectField(
        label="Select Address",
        choices=[
            ("aaa", "<<< Lookup"),
        ],
        description="",
    )
    applyAddress = SubmitField(label="Apply")
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
    language = SelectField(
        label="language",
        validators=[Optional()
            , Regexp( "^EN$", message="Choose EN or none, defaults to FR")
            , Length(1, 30)],
        choices=[
            ("", "FR"),
            ("EN", "EN"),
        ],
        description="",
    )
    paymentMethod = SelectField(
        label="paymentMethod",
        validators=[Optional()
            , Regexp(
                "^(VISA|MC)$", message="Choose VISA or MC or none"
            )
            , Length(1, 30)],
        choices=[
            ("VISA", "VISA"),
            ("MC", "MC"),
            ("", "Cheque"),
        ],
        description="",
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
        validators=[InputRequired(), Length(1, 250)],
        description="",
        render_kw={"placeholder": "notes"},
    )
    dateJoined = StringField(
        label="dateJoined",
        validators=[InputRequired(), Length(1, 30)],
        description="",
        render_kw={"placeholder": "dateJoined"},
    )
    updateUser = SubmitField(label="Update")


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
    app.config["HTTP_USER"] = os.environ.get("HTTP_USER")
    app.config["HTTP_PASS"] = os.environ.get("HTTP_PASS")

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    bootstrap = Bootstrap5(app)

    auth = HTTPBasicAuth()
    if app.config["HTTP_USER"] and app.config["HTTP_PASS"]:
        authorizedUsers = {
            app.config["HTTP_USER"]: generate_password_hash(app.config["HTTP_PASS"])
        }
    else:
        authorizedUsers = None

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
        # check dbLink is iterable i.e. not using fake_mssql
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

    def isUserExist(loginName):
        isUserExist = None
        if loginName:
            isUserExist = queryDBscalar(
                """SELECT count(*) as 'counter'
                 FROM UsersId
                 WHERE lower(LoginName) = lower(%s)""",
                loginName,
            )
        return isUserExist

    @auth.verify_password
    def verify_password(username, password):
        if authorizedUsers is None:
            return True

        if username in authorizedUsers and check_password_hash(
            authorizedUsers.get(username), password
        ):
            return username

    @app.route("/")
    @auth.login_required
    def index():
        return render_template("index.html")

    @app.route("/form", methods=["GET", "POST"])
    @auth.login_required
    def test_form():
        formSearchLogin = FormSearchLogin(request.args)
        formUserDetail = FormUserDetail()

        if request.method == "GET" and request.args.get("LoginName") is not None:
            formSearchLogin.loginName.data = request.args.get("LoginName")

        if (
            request.method == "GET"
            and "loginName" in request.args
            and formSearchLogin.validate()
            and isUserExist(formSearchLogin.data["loginName"]) == 1
        ):
            flash("Debug: indicating location AAA ....", "warning")
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
                  isnull(Language, '') as 'Language',
                  isnull(PaymentMethod, '') as 'PaymentMethod',
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
            formUserDetail.loginName.data = str(formSearchLogin.data["loginName"])
            formUserDetail.firstName.data = str(usersDict["FirstName"])
            formUserDetail.lastName.data = str(usersDict["LastName"])
            formUserDetail.organizationName.data = str(usersDict["OrganizationName"])
            formUserDetail.address.data = str(usersDict["Address"])
            formUserDetail.city.data = str(usersDict["City"])
            formUserDetail.state.data = str(usersDict["State"])
            formUserDetail.postalCode.data = str(usersDict["PostalCode"])
            formUserDetail.country.data = str(usersDict["Country"])
            formUserDetail.homePhone.data = str(usersDict["HomePhone"])
            formUserDetail.accountNumber.data = str(usersDict["AccountNumber"])
            formUserDetail.language.process_data(str(usersDict["Language"]).strip())
            formUserDetail.paymentMethod.process_data(str(usersDict["PaymentMethod"].strip()))
            formUserDetail.creditCardNumber.data = str(usersDict["CreditCardNumber"])
            formUserDetail.creditCardExpiry.data = str(usersDict["CreditCardExpiry"])
            formUserDetail.bankName.data = str(usersDict["BankName"])
            formUserDetail.checkNumber.data = str(usersDict["CheckNumber"])
            formUserDetail.bankAccount.data = str(usersDict["BankAccount"])
            formUserDetail.identificationCard.data = str(
                usersDict["IdentificationCard"]
            )
            formUserDetail.authorizationCode.data = str(usersDict["AuthorizationCode"])
            formUserDetail.operatingSystem.data = str(usersDict["OperatingSystem"])
            formUserDetail.operator.data = str(usersDict["Operator"])
            formUserDetail.referredBy.data = str(usersDict["ReferredBy"])
            formUserDetail.notes.data = str(usersDict["Notes"])
            formUserDetail.dateJoined.data = str(usersDict["DateJoined"])

        if (
            request.method == "POST"
            and formUserDetail.lookupAddress.data
            and formUserDetail.postalCode.data
        ):
            flash("Debug: indicating location 'lookupAddress' ....", "warning")
            flash(f"Debug: {formUserDetail.postalCode.data}", "warning")
            indexID = getIndexFromPostal(formUserDetail.postalCode.data)
            listOfAddresses = getIDsFromIndex(indexID)
            myChoices = [
                ("", "Refine address ..."),
            ]
            myChoices += [(k, v) for k, v in listOfAddresses.items()]
            formUserDetail.addressSelect.choices = myChoices

        if (
            request.method == "POST"
            and formUserDetail.applyAddress.data
            and formUserDetail.addressSelect.data
        ):
            flash("Debug: indicating location 'applyAddress' ....", "warning")
            flash(f"Debug: {formUserDetail.addressSelect.data}", "warning")
            postalAddress = getAddressFromID(formUserDetail.addressSelect.data)
            if len(postalAddress) >= 5:
                formUserDetail.address.data = postalAddress["Line1"]
                formUserDetail.city.data = postalAddress["City"]
                formUserDetail.state.data = postalAddress["ProvinceCode"]
                formUserDetail.country.data = "Canada"
                formUserDetail.postalCode.data = postalAddress["PostalCode"]
                flash(f"address applied: {formUserDetail.address.data}", "primary")

        if (
            request.method == "POST"
            and formUserDetail.updateUser.data
            and formUserDetail.validate_on_submit()
        ):
            flash("Debug: indicating location 'updateUser' ....", "warning")
            try:
                """
                formUserDetail.populate_obj(userInfoModel)
                db.session.add(userInfoModel)
                db.session.commit()
                """
                flash('LoginName="' + formUserDetail.data["loginName"] + '"', "success")
            except:
                # db.session.rollback()
                flash("Error: could not save.", "danger")

        return render_template(
            "form.html",
            formSearchLogin=formSearchLogin,
            formUserDetail=formUserDetail,
            isUserExist=isUserExist(formSearchLogin.data["loginName"]),
        )

    return app


# if __name__ == "__main__":
#    app.run(debug=True)
