# -*- coding: utf-8 -*-
""" Updateuser

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

updateuser = Blueprint("updateuser", __name__)


class FormSearchLogin(FlaskForm):
    class Meta:
        csrf = False

    loginName = StringField(
        label="Login name",
        validators=[
            InputRequired(),
            Regexp(
                "^[a-z0-9][a-z0-9.-]*$",
                flags=re.IGNORECASE,
                message="incorrect characters used",
            ),
            Length(1, 20),
        ],
        description="",
        render_kw={"placeholder": "Customer username"},
    )
    submit = SubmitField(label="Search")


class FormUserDetail(FlaskForm):
    loginName = HiddenField(
        label="Login name",
        validators=[
            InputRequired(),
            Length(1, 20),
            Regexp("^[a-z0-9][a-z0-9.-]*$", message="incorrect characters used"),
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
    accountNumber = StringField(
        label="accountNumber",
        validators=[
            InputRequired(),
            Length(1, 30),
            Regexp(
                "^[0-9]{1,9}$",
                message="must be 9-digit ex. 800-555-1234 becomes 855512341",
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
    creditCardNumber = StringField(
        label="creditCardNumber",
        validators=[
            Optional(),
            Length(1, 30),
            Regexp(
                "^[0-9 ]{16,19}$",
                message="must be empty or a credit card number 4111111111111111",
            ),
        ],
        description="",
        render_kw={"placeholder": ""},
    )

    def validate_creditCardNumber(form, field):
        if not form.creditCardExpiry.data:
            raise ValidationError("missing credit card expiration date")

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

    def validate_creditCardExpiry(form, field):
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

        if field.data and not _isDateValid(field.data):
            raise ValidationError("CC Exp is invalid or expired")
        if not form.creditCardNumber.data:
            raise ValidationError("missing credit cardnumber")

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
    operatingSystem = StringField(
        label="operatingSystem",
        validators=[
            Optional(),
            Length(1, 10),
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
            InputRequired(),
            Length(1, 250),
            Regexp(
                "^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$", message="incorrect characters used"
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
    updateUser = SubmitField(label="Update")


auth = HTTPBasicAuth()
if current_app.config["HTTP_USER"] and current_app.config["HTTP_PASS"]:
    authorizedUsers = {
        current_app.config["HTTP_USER"]: generate_password_hash(
            current_app.config["HTTP_PASS"]
        )
    }
else:
    authorizedUsers = None


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


@auth.verify_password
def verify_password(username, password):
    if authorizedUsers is None:
        return True

    if username in authorizedUsers and check_password_hash(
        authorizedUsers.get(username), password
    ):
        return username


@updateuser.route("/test")
def testroute():
    myVar = current_app.config["DB_IP"]
    return f"<h1>{myVar} Hurrah!!</h1>"


@updateuser.route("/", methods=["GET", "POST"])
@auth.login_required
def updateuser_form():
    formSearchLogin = FormSearchLogin(request.args)
    formUserDetail = FormUserDetail()

    """ URL contains ?LoginName=someuser """
    if request.method == "GET" and request.args.get("LoginName") is not None:
        formSearchLogin.loginName.data = request.args.get("LoginName")

    """ Button Pressed SEARCH Login """
    if (
        request.method == "GET"
        and "loginName" in request.args
        and formSearchLogin.validate()
        and isUserExist(formSearchLogin.data["loginName"]) == 1
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
              replace(convert(varchar,DateJoined,102),'.','-') as "DateJoined"
          FROM
              UsersId
          WHERE
              LoginName = %s
          """,
            formSearchLogin.data["loginName"],
        )
        formUserDetail = FormUserDetail()
        formUserDetail.loginName.data = str(formSearchLogin.data["loginName"] or "")
        formUserDetail.firstName.data = str(usersDict["FirstName"] or "")
        formUserDetail.lastName.data = str(usersDict["LastName"] or "")
        formUserDetail.organizationName.data = str(usersDict["OrganizationName"] or "")
        formUserDetail.address.data = str(usersDict["Address"] or "")
        formUserDetail.city.data = str(usersDict["City"] or "")
        formUserDetail.state.data = str(usersDict["State"] or "")
        formUserDetail.postalCode.data = str(usersDict["PostalCode"] or "")
        formUserDetail.country.data = str(usersDict["Country"] or "")
        formUserDetail.homePhone.data = str(usersDict["HomePhone"] or "")
        formUserDetail.accountNumber.data = str(usersDict["AccountNumber"] or "")
        formUserDetail.language.process_data(str(usersDict["Language"]).strip())
        formUserDetail.paymentMethod.process_data(
            str(usersDict["PaymentMethod"].strip())
        )
        formUserDetail.creditCardNumber.data = str(usersDict["CreditCardNumber"] or "")
        formUserDetail.creditCardExpiry.data = _sanitizeCreditCardExpiry(
            str(usersDict["CreditCardExpiry"] or "")
        )
        formUserDetail.bankName.data = str(usersDict["BankName"] or "")
        formUserDetail.checkNumber.data = str(usersDict["CheckNumber"] or "")
        formUserDetail.bankAccount.data = str(usersDict["BankAccount"] or "")
        formUserDetail.identificationCard.data = str(
            usersDict["IdentificationCard"] or ""
        )
        formUserDetail.authorizationCode.data = str(
            usersDict["AuthorizationCode"] or ""
        )
        formUserDetail.operatingSystem.data = str(usersDict["OperatingSystem"] or "")
        formUserDetail.operator.process_data(str(usersDict["Operator"]).strip())
        formUserDetail.referredBy.data = str(usersDict["ReferredBy"] or "")
        formUserDetail.notes.data = str(usersDict["Notes"] or "")
        formUserDetail.dateJoined.data = str(usersDict["DateJoined"] or "")

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

    """ Button Pressed UPDATE Userinfo """
    if (
        request.method == "POST"
        and formUserDetail.updateUser.data
        and formUserDetail.validate_on_submit()
    ):
        try:
            updateAladinSQL1 = f"""
            EXECUTE UpdateUserFile
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
                , @OperatingSystem = %s
                , @AccountNumber = %s
                , @PaymentMethod = %s
                , @Membership = %s
                , @CreditCardExpiry = %s
                , @CreditCardNumber = %s
                , @Notes = %s
                , @DateJoined = %s
                , @NextBilling = %s
                , @AccountSetupBy = %s
                , @ReferredBy = %s
                , @GovID = %s
                , @GovConfirmation = %s
                , @GovAmount = %s
                , @OneTimeCharge = %s
                , @OneTimeQty = %s
                , @Language = %s
                , @DebugLevel = %d
                , @Operator = %s
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
        	    , {formUserDetail.data["operatingSystem"]}
        	    , {formUserDetail.data["accountNumber"]}
        	    , {formUserDetail.data["paymentMethod"]}
        	    ,
        	    , {creditCardExpiry}
        	    , {formUserDetail.data["creditCardNumber"]}
        	    , {formUserDetail.data["notes"]}
        	    , {formUserDetail.data["dateJoined"]}
        	    ,
        	    ,
        	    , {formUserDetail.data["referredBy"]}
        	    ,
        	    ,
        	    ,
        	    ,
        	    ,
        	    , {formUserDetail.data["language"]}
        	    , 1
        	    , {formUserDetail.data["operator"]}
                """
            updateAladinSQL2 = f"""
                UPDATE UsersId SET
        	    BankName = %s
        	    , CheckNumber = %s
        	    , BankAccount = %s
        	    , IdentificationCard = %s
        	    , AuthorizationCode = %s
                WHERE LoginName = %s
                """
            updateAladinParam2 = f"""
        	    {formUserDetail.data["bankName"]}
        	    , {formUserDetail.data["checkNumber"]}
        	    , {formUserDetail.data["bankAccount"]}
        	    , {formUserDetail.data["identificationCard"]}
        	    , {formUserDetail.data["authorizationCode"]}
        	    , {formUserDetail.data["loginName"]}
               """
            flash(updateAladinSQL1, "success")
            flash(updateAladinParam1, "success")
            flash(updateAladinSQL2, "success")
            flash(updateAladinParam2, "success")
            # disable form after update completed
            formSearchLogin.loginName.data = ""
        except:
            flash("Error: could not save.", "danger")

    return render_template(
        "updateuser.html",
        formSearchLogin=formSearchLogin,
        formUserDetail=formUserDetail,
        isUserExist=isUserExist(formSearchLogin.data["loginName"]),
    )
