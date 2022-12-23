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
from src.model import queryDBscalar, queryDBrow
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
    """ --- """
    """ URL contains ?LoginName=someuser """
    if request.method == "GET" and request.args.get("LoginName") is not None:
        formUserDetail.loginName.data = request.args.get("LoginName")
    """ --- """
    """ Button Pressed Search userinvoice """
    if (
        request.method == "POST"
        and formUserDetail.userInvoice.data
        and formUserDetail.validate_on_submit()
    ):
        try:
            updateAladinSQL1 = f"""
            EXECUTE UserInvoice
                @LoginName = %s
                """
            updateAladinParam1 = f"""
                    {formUserDetail.data["loginName"]}
                """
            flash(f"{formUserDetail.data['loginName']} queried successfully","success") 
            flash(updateAladinSQL1, "success")
            flash(updateAladinParam1, "success")
        except:
            flash("Error: could not find invoice.", "danger")
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
