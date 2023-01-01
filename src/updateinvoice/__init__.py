# -*- coding: utf-8 -*-
""" updateinvoice

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
from src.model import queryDBscalar, queryDBrow, queryDBall

""" --- """
""" define url http://.../updateinvoice/ """
updateinvoice = Blueprint("updateinvoice", __name__)


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
""" Class used to generate FORM SearchInvoice """
class FormSearchInvoice(FlaskForm):
    """ disable csrf for this form """
    class Meta:
        csrf = False

    loginName = StringField(
        label="Invoice Number",
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
        render_kw={"placeholder": "Invoice number"},
    )
    submit = SubmitField(label="Search")


""" --- """
""" Class used to generate FORM UserDetail """
class FormUserInvoice(FlaskForm):
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
    invoiceDateStart = StringField(
        label="Invoice Date Start",
        validators=[
            Optional(),
            Length(10, 10),
            Regexp("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", message="YYYY-MM-DD ex:2030-11-30"),
        ],
        description="",
        render_kw={"placeholder": ""},
    )
    updateInvoice = SubmitField(label="Update Invoice",
        render_kw={"accesskey": "s", "title": "alt-S / ctrl-alt-S"},
    )


""" --- """
""" URL contains ?LoginName=someuser """
def _assignLoginFromUrl(formUserInvoice):
    if request.method == "GET" and request.args.get("LoginName"):
        formUserInvoice.loginName.data = request.args.get("LoginName")


""" --- """
""" DB getUserInvoice  """
def _getUserInvoice(formUserInvoice):
    allRows = None
    try:
        updateAladinSQL1 = f"""
            EXECUTE UserInvoice
            @LoginName = %s
            """
        updateAladinParam1 = ( formUserInvoice.data["loginName"] , )
        allRows = queryDBall(updateAladinSQL1, updateAladinParam1)
    except:
        flash("Error: could not get User Invoice.", "danger")
    return allRows


""" --- """
""" returns list of invoices used by user  """
def _getUniqueInvoices( userInvoices ):
    invoiceNumbers = set([])
    for eachRow in userInvoices:
        invoiceNumbers.add( eachRow['InvoiceNumber'] )
    return invoiceNumbers


""" --- """
""" DB getUserInvoiceDetail  """
""" get invoicedetail for each invoice """
def _getUserInvoiceDetail(allUserInvoices):
    invoiceNumbers = _getUniqueInvoices(allUserInvoices)
    userInvoicesDetails={}
    for eachInvoiceNumber in invoiceNumbers:
        allRows = None
        try:
            updateAladinSQL1 = f"""
                EXECUTE UserInvoiceDetail
                @InvoiceNumber = %s
                """
            updateAladinParam1 = ( eachInvoiceNumber , )
            allRows = queryDBall(updateAladinSQL1, updateAladinParam1)
            userInvoicesDetails[eachInvoiceNumber] = allRows
        except:
            flash("could not get User Invoice Detail: {eachInvoiceNumber}", "danger")
    return userInvoicesDetails


""" --- """
""" DB getUpdateUsersPlans  """
def _getUpdateUsersPlans(loginName = ''):
    allRows = []
    try:
        updateAladinSQL1 = f"""
            EXECUTE UpdateUsersPlans
            @LoginName = %s
            """
        updateAladinParam1 = loginName or " "
        allRows = queryDBall(updateAladinSQL1, updateAladinParam1)
    except:
        flash("Error: could not get info from UpdateUsersPlans.", "danger")
    return allRows


""" --- """
""" Button Pressed Search updateinvoice """
def _processFormSubmit(formUserDetail):
    queryResult = {}
    if (
        request.method == "POST"
        and formUserDetail.updateInvoice.data
        and formUserDetail.validate_on_submit()
    ):
        queryResult["UserInvoice"] = _getUserInvoice(formUserDetail)
        allUserInvoices = queryResult["UserInvoice"]
        queryResult["UserInvoiceDetail"] = _getUserInvoiceDetail(allUserInvoices)
        """ --- """
        """ get loginName from previous Invoices list """
        actualLoginName = None
        if len(allUserInvoices) > 1:
            actualLoginName = allUserInvoices[0]["LoginName"]
        queryResult["UpdateUsersPlans"] = _getUpdateUsersPlans(actualLoginName)
        return queryResult


""" --- """
""" simpleCrypt encrypt/decrypt with XOR """
def simpleCrypt(varToCrypt=''):
    simpleCrypt = ''
    for i in range(len(varToCrypt) -1, -1, -1):
        simpleCrypt = simpleCrypt + chr(ord(varToCrypt[i]) ^ 22)
    return simpleCrypt

""" --- """
""" browser clicked updateinvoice/test """
@updateinvoice.route("/test")
def testroute():
    myVar = current_app.config["DB_IP"]
    return f"<h1>{myVar} Hurrah!!</h1>"


""" --- """
""" browser clicked updateinvoice/ """
@updateinvoice.route("/", methods=["GET", "POST"])
@auth.login_required
def updateinvoice_form():
    formUserInvoice = FormUserInvoice()
    _assignLoginFromUrl(formUserInvoice)

    """ --- """
    """ display page """
    loginName = formUserInvoice.data["loginName"] or ""
    domain = current_app.config["DOMAIN"] or "example.com"
    urlQuery = f"LoginName={loginName}"
    invoices = _processFormSubmit(formUserInvoice)
    return render_template(
        "updateinvoice.html",
        formUserInvoice=formUserInvoice,
        domain=domain,
        urlQuery=urlQuery,
        invoices=invoices,
        simpleCrypt=simpleCrypt
    )
