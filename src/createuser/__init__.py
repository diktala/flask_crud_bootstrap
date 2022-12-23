# -*- coding: utf-8 -*-
""" Createuser

This flask page uses Flask and WTF and pymssql to update Aladin
It is a flask-blueprint called from app.py

Example:
    python
    [...]

Attributes:
    [...]
"""
import re
from datetime import timedelta, datetime as dt
from flask import Flask, current_app, Blueprint, render_template, request, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import InputRequired, Optional, Length, Regexp, ValidationError
from wtforms.fields import *
from src.model import queryDBscalar, queryDBrow
from src.canadapost import getIDsFromIndex, getIndexFromPostal, getAddressFromID

""" --- """
""" define url http://.../createuser/ """
createuser = Blueprint("createuser", __name__)


""" --- """
""" load user info HTTPBasicAuth """
auth = HTTPBasicAuth()
if current_app.config["HTTP_USER"] and current_app.config["HTTP_PASS"]:
    authorizedUsers = {
        current_app.config["HTTP_USER"]: generate_password_hash(
            current_app.config["HTTP_PASS"]
        )
    }
else:
    authorizedUsers = None


""" --- """
""" check http user (called by decorator @auth.login_required) """


@auth.verify_password
def verify_password(username, password):
    if authorizedUsers is None:
        return True
    """ --- """
    """ enforce http auth only if env HTTP_USER is defined """
    if username in authorizedUsers and check_password_hash(
        authorizedUsers.get(username), password
    ):
        return username


""" --- """
""" Class used to generate FORM UserDetail """
class FormUserDetail(FlaskForm):
    loginName = StringField(
        label="Login name",
        validators=[
            InputRequired(),
            Length(1, 20),
            Regexp("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    """ --- """
    """ validate LoginName is available """
    def validate_loginName(form, field):
        if field.data and _isUserExist(field.data):
            raise ValidationError("This username is not available")
    userPassword = StringField(
        label="User password",
        validators=[
            InputRequired(),
            Length(1, 12),
            Regexp("^[\w.-]+$", message="characters allowed: a-z 0-9 . - "),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    firstName = StringField(
        label="First name",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp("^[\w. &'-]*[\w]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    lastName = StringField(
        label="Last name",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp("^[\w. &'-]*[\w]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    organizationName = StringField(
        label="organizationName",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    address = StringField(
        label="address",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp("^[\w. &/'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    city = StringField(
        label="city",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp("^[\w. &'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    state = StringField(
        label="state",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp("^[\w. &'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    postalCode = StringField(
        label="postalCode",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp(
                "^[A-Z][0-9][A-Z] [0-9][A-Z][0-9]$",
                message="must use a canadian postal code H1H 1H1",
            ),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    lookupAddress = SubmitField(label="Lookup")
    addressSelect = SelectField(
        label="Select Address",
        choices=[
            ("", "<<< Lookup"),
        ],
        description="",
    )
    applyAddress = SubmitField(label="Apply")
    country = StringField(
        label="country",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp("^[\w. &'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    homePhone = StringField(
        label="homePhone",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp(
                "^[0-9]{3} [0-9]{3} [0-9]{4}$", message="must use format 514 555 1212"
            ),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    language = SelectField(
        label="language",
        validators=[
            Optional(),
            Regexp("^EN$", message="Choose EN or none, defaults to FR"),
            Length(1, 30),
        ],
        choices=[
            ("", "FR"),
            ("EN", "EN"),
        ],
        description="",
    )
    paymentMethod = SelectField(
        label="paymentMethod",
        validators=[
            Optional(),
            Regexp("^(VISA|MC)$", message="Choose VISA or MC or none"),
            Length(1, 30),
        ],
        choices=[
            ("VISA", "VISA"),
            ("MC", "MC"),
            ("", "Cheque"),
        ],
        description="",
    )
    """ --- """
    """ validate paymentMethod WTForms """

    def validate_paymentMethod(form, field):
        if form.paymentMethod.data and not form.creditCardNumber.data:
            raise ValidationError("missing credit card number")

    """ --- """
    creditCardNumber = StringField(
        label="creditCardNumber",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp(
                "^[0-9]{16}$",
                message="must be empty or a credit card number 4111111111111111",
            ),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    """ --- """
    """ validate creditCardNumber WTForms """

    def validate_creditCardNumber(form, field):
        if not form.creditCardExpiry.data:
            raise ValidationError("missing credit card expiration date")
        if not form.paymentMethod.data:
            raise ValidationError("select credit card type")

    """ --- """
    creditCardExpiry = StringField(
        label="creditCardExpiry",
        validators=[
            Optional(),
            Length(10, 10),
            Regexp("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", message="YYYY-MM-DD ex:2030-11-30"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    """ --- """
    """ validate creditCardExpiry WTForms """

    def validate_creditCardExpiry(form, field):
        """---"""
        """ check if date is valid otherwise return False """

        def _isDateValid(stringDate=""):
            output = False
            try:
                myDate = dt.strptime(stringDate, "%Y-%m-%d")
                nowDate = dt.today()
                if myDate > nowDate:
                    output = True
            except:
                pass
            return output

        """ --- """
        if field.data and not _isDateValid(field.data):
            raise ValidationError("CC Exp is invalid or expired")
        if not form.creditCardNumber.data:
            raise ValidationError("missing credit cardnumber")

    """ --- """
    bankName = StringField(
        label="bankName",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &/'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    checkNumber = StringField(
        label="checkNumber",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &/'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    bankAccount = StringField(
        label="bankAccount",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &/'-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    identificationCard = StringField(
        label="identificationCard",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &/'#:-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    authorizationCode = StringField(
        label="authorizationCode",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &/'#:-]*[\w.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    operatorNames = current_app.config["OPERATORS"] or "Other"
    operator = SelectField(
        label="operator",
        choices=[(op, op) for op in operatorNames.split(" ")],
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w.-]*$", message="incorrect characters used"),
        ],
        description="",
    )
    referredBy = StringField(
        label="referredBy",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp("^[\w. &/'#:-]*[\w:.]$", message="incorrect characters used"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    notes = StringField(
        label="notes",
        validators=[
            Optional(),
            Length(1, 250),
            Regexp(
                "^[\w.-]*$", message="incorrect characters used"
            ),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    dateJoined = HiddenField(
        label="dateJoined",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp(
                "^[0-9]{4}-[0-9]{2}-[0-9]{2}( 00:00:00)?$",
                message="incorrect characters used 2000-01-01",
            ),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    createUser = SubmitField(label="Create",
        render_kw={"accesskey": "s", "title": "alt-S / ctrl-alt-S"},
    )


""" --- """
""" check if user Exist, returns None otherwise """


def _isUserExist(loginName):
    isUserExist = None
    if loginName:
        isUserExist = queryDBscalar(
            """SELECT COUNT(*) AS 'counter'
                FROM SecondaryMailbox
                WHERE MainLoginName = lower( %(loginname1)s )
                      OR MailBox = lower( %(loginname2)s )
             """,
            dict(loginname1=loginName, loginname2=loginName),
        )
    return isUserExist


""" --- """
""" sanitize credit card expiry """


def _sanitizeCreditCardExpiry(ccExp=""):
    output = ""
    try:
        ccExpTrimmed = re.sub(r"^([0-9]+-[0-9]+-[0-9]+)( .*)", r"\1", ccExp)
        expirationDate = dt.strptime(ccExpTrimmed, "%Y-%m-%d")
        #
        # get close to the end of month and add 4 days over
        next_month = expirationDate.replace(day=28) + timedelta(days=4)
        last_day_of_month = next_month - timedelta(days=next_month.day)
        output = last_day_of_month.strftime("%Y-%m-%d")
    except:
        pass
    return output


""" --- """
""" browser clicked createuser/test """


@createuser.route("/test")
def testroute():
    myVar = current_app.config["DB_IP"]
    return f"<h1>{myVar} Hurrah!!</h1>"


""" --- """
""" browser clicked createuser/ """
@createuser.route("/", methods=["GET", "POST"])
@auth.login_required
def createuser_form():
    formUserDetail = FormUserDetail()
    """ --- """
    """ URL contains ?LoginName=someuser """
    if request.method == "GET" and request.args.get("LoginName") is not None:
        formUserDetail.loginName.data = request.args.get("LoginName")
    """ --- """
    """ Button Pressed LOOKUP postal code """
    if (
        request.method == "POST"
        and formUserDetail.lookupAddress.data
        and formUserDetail.postalCode.data
    ):
        indexID = getIndexFromPostal(formUserDetail.postalCode.data)
        listOfAddresses = getIDsFromIndex(indexID)
        myChoices = [
            ("", "Refine address ..."),
        ]
        myChoices += [(k, v) for k, v in listOfAddresses.items()]
        formUserDetail.addressSelect.choices = myChoices
    """ --- """
    """ Button Pressed APPLY postal code """
    if (
        request.method == "POST"
        and formUserDetail.applyAddress.data
        and formUserDetail.addressSelect.data
    ):
        postalAddress = getAddressFromID(formUserDetail.addressSelect.data)
        if len(postalAddress) >= 5:
            formUserDetail.address.data = postalAddress["Line1"]
            formUserDetail.city.data = postalAddress["City"]
            formUserDetail.state.data = postalAddress["ProvinceCode"]
            formUserDetail.country.data = "Canada"
            formUserDetail.postalCode.data = postalAddress["PostalCode"]
            flash(f"address applied: {formUserDetail.address.data}", "primary")
    """ --- """
    """ Button Pressed Create Userinfo """
    if (
        request.method == "POST"
        and formUserDetail.createUser.data
        and formUserDetail.validate_on_submit()
    ):
        try:
            updateAladinSQL1 = f"""
            EXECUTE CreateUser
                @LoginName = %s
                , @FirstName = %s
                , @LastName = %s
                , @OrganizationName = %s
                , @Address = %s
                , @City = %s
                , @State = %s
                , @PostalCode = %s
                , @Country = %s
                , @HomePhone = %s
                , @Membership = %s
                , @Notes = %s
                , @UserPassword = %s
                , @OperatingSystem = %s
                , @AccountNumberChr = %s
                , @PaymentMethod = %s
                , @CreditCardExpiry = %s
                , @CreditCardNumber = %s
                , @CurrentPlan = %s
                , @BankName = %s
                , @CheckNumber = %s
                , @BankAccount = %s
                , @IdentificationCard = %s
                , @AuthorizationCode = %s
                , @Operator = %s
                , @ReferredBy = %s
                , @GovID = %s
                , @GovConfirmation = %s
                , @GovAmount = %s
                """
            creditCardExpiry = _sanitizeCreditCardExpiry(
                formUserDetail.data["creditCardExpiry"]
            )
            updateAladinParam1 = f"""
                    {formUserDetail.data["loginName"]}
                    , {formUserDetail.data["firstName"]}
                    , {formUserDetail.data["lastName"]}
                    , {formUserDetail.data["organizationName"]}
                    , {formUserDetail.data["address"]}
                    , {formUserDetail.data["city"]}
                    , {formUserDetail.data["state"]}
                    , {formUserDetail.data["postalCode"]}
                    , {formUserDetail.data["country"]}
                    , {formUserDetail.data["homePhone"]}
                    ,
                    , {formUserDetail.data["notes"]}
                    , {formUserDetail.data["userPassword"]}
                    ,
                    ,
                    , {formUserDetail.data["paymentMethod"]}
                    , {creditCardExpiry}
                    , {formUserDetail.data["creditCardNumber"]}
                    ,
                    , {formUserDetail.data["bankName"]}
                    , {formUserDetail.data["checkNumber"]}
                    , {formUserDetail.data["bankAccount"]}
                    , {formUserDetail.data["identificationCard"]}
                    , {formUserDetail.data["authorizationCode"]}
                    , {formUserDetail.data["operator"]}
                    , {formUserDetail.data["referredBy"]}
                    ,
                    ,
                    ,
                """
            flash(f"{formUserDetail.data['loginName']} added successfully","success") 
            flash(updateAladinSQL1, "success")
            flash(updateAladinParam1, "success")
        except:
            flash("Error: could not create user.", "danger")
    """ --- """
    """ display page """
    loginName = formUserDetail.data["loginName"] or ""
    domain = current_app.config["DOMAIN"] or "example.com"
    urlQuery = f"LoginName={loginName}"
    return render_template(
        "createuser.html",
        formUserDetail=formUserDetail,
        domain=domain,
        urlQuery=urlQuery,
    )
