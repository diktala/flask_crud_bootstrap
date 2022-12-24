# -*- coding: utf-8 -*-
""" userinvoice

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
from src.canadapost import getIDsFromIndex, getIndexFromPostal, getAddressFromID

""" --- """
""" define url http://.../userinvoice/ """
userinvoice = Blueprint("userinvoice", __name__)


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
    userInvoice = SubmitField(label="Search",
        render_kw={"accesskey": "s", "title": "alt-S / ctrl-alt-S"},
    )


""" --- """
""" URL contains ?LoginName=someuser """
def _assignLoginFromUrl(formUserDetail):
    if request.method == "GET" and request.args.get("LoginName"):
        formUserDetail.loginName.data = request.args.get("LoginName")


""" --- """
""" DB getUserInvoice  """
def _getUserInvoice(formUserDetail):
    allRows = None
    try:
        updateAladinSQL1 = f"""
            EXECUTE UserInvoice
            @LoginName = %s
            """
        updateAladinParam1 = ( formUserDetail.data["loginName"] , )
        allRows = queryDBall(updateAladinSQL1, updateAladinParam1)
        flash(f"UserInvoice queried successfully","success")
    except:
        flash("Error: could not get User Invoice.", "danger")
    return allRows


def _getUniqueInvoices( userInvoices ):
    invoiceNumbers = set([])
    for eachRow in userInvoices.values():
        invoiceNumbers.add( eachRow['InvoiceNumber'] )
    return invoiceNumbers


""" --- """
""" DB getUserInvoiceDetail  """
def _getUserInvoiceDetail(allUserInvoices):
    # invoiceNumber = allUserInvoices[0]["InvoiceNumber"]
    invoiceNumbers = _getUniqueInvoices(allUserInvoices)
    """ get invoicedetail for each invoice """
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
def _getUpdateUsersPlans(formUserDetail):
    allRows = None
    try:
        updateAladinSQL1 = f"""
            EXECUTE UpdateUsersPlans
            @LoginName = %s
            """
        updateAladinParam1 = ( formUserDetail.data["loginName"] , )
        allRows = queryDBall(updateAladinSQL1, updateAladinParam1)
        flash(f"UpdateUsersPlans queried successfully","success")
    except:
        flash("Error: could not get info from UpdateUsersPlans.", "danger")
    return allRows


""" --- """
""" Button Pressed Search userinvoice """
def _processFormSubmit(formUserDetail):
    queryResult = {}
    if (
        request.method == "POST"
        and formUserDetail.userInvoice.data
        and formUserDetail.validate_on_submit()
    ):
        queryResult["UserInvoice"] = _getUserInvoice(formUserDetail)
        allUserInvoices = queryResult["UserInvoice"]
        queryResult["UserInvoiceDetail"] = _getUserInvoiceDetail(allUserInvoices)
        queryResult["UpdateUsersPlans"] = _getUpdateUsersPlans(formUserDetail)
        # assert False
        flash(f"queryResult {queryResult}","success")
        return queryResult


""" --- """
""" browser clicked userinvoice/test """
@userinvoice.route("/test")
def testroute():
    myVar = current_app.config["DB_IP"]
    return f"<h1>{myVar} Hurrah!!</h1>"


""" --- """
""" browser clicked userinvoice/ """
@userinvoice.route("/", methods=["GET", "POST"])
@auth.login_required
def userinvoice_form():
    formUserDetail = FormUserDetail()
    _assignLoginFromUrl(formUserDetail)
    queryResult = _processFormSubmit(formUserDetail)
    # flash(queryResult, "warning")

    """ --- """
    """ display page """
    loginName = formUserDetail.data["loginName"] or ""
    domain = current_app.config["DOMAIN"] or "example.com"
    urlQuery = f"LoginName={loginName}"
    return render_template(
        "userinvoice.html",
        formUserDetail=formUserDetail,
        domain=domain,
        urlQuery=urlQuery,
    )
