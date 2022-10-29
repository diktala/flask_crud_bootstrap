# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, Markup, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'dev'
# set bootstrap to be served locally 
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap5(app)
db = SQLAlchemy(app)
# csrf = CSRFProtect(app)


class DB_User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loginName = db.Column(db.String(30), nullable=False)
    firstName = db.Column(db.String(30), nullable=False)
    lastName = db.Column(db.String(30), nullable=False)


class FormSearchLogin(FlaskForm):
    loginName = StringField(  label='Login name'
                            , validators=[DataRequired()
                            , Length(1, 20)]
                            , description=''
                            , render_kw={"placeholder": "Customer username"}
                )
    firstName = StringField(  label='First name'
                            , validators=[DataRequired()
                            , Length(1, 20)]
                            , description=''
                            , render_kw={"placeholder": "Customer first name"}
                )
    lastName = StringField(  label='Last name'
                            , validators=[DataRequired()
                            , Length(1, 20)]
                            , description=''
                            , render_kw={"placeholder": "Customer last name"}
                )
    submit = SubmitField()



@app.before_first_request
def before_first_request_func():
    db.drop_all()
    db.create_all()
    names = {"alpha","bravo","charly"}
    for name in names:
        row = DB_User(
            loginName=f'{name}',
            firstName=f'{name} First',
            lastName=f'{name} Last',
            )
        db.session.add(row)
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def test_form():
    exampleUser = DB_User.query.filter_by(id=3).first()
    form = FormSearchLogin(obj=exampleUser)
    if ( request.method == 'GET'
         and request.args.get('LoginName') is not None
        ):
        form.loginName.data = request.args.get('LoginName')

    if form.validate_on_submit():
        try:
            form.populate_obj(exampleUser)
            db.session.add(exampleUser)
            db.session.commit()
            flash('LoginName="' + form.data['loginName'] + '"', 'success')
            return redirect(url_for('test_form'))
        except:
            db.session.rollback()
            flash('Error: could not save.', 'danger')

    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
