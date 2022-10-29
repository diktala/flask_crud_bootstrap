# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, Markup, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_bootstrap import Bootstrap5, SwitchField

app = Flask(__name__)
app.secret_key = 'dev'
# set bootstrap to be served locally 
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['WTF_CSRF_ENABLED'] = False

bootstrap = Bootstrap5(app)
# csrf = CSRFProtect(app)

class DB_User():
    loginName = 'some-user'
    password = 'some-password'
    remember = True

class FormSearchLogin(FlaskForm):
    loginName = StringField(label='Login name', validators=[DataRequired(), Length(1, 20)], description="", render_kw={"placeholder": "Customer username"} )
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def test_form():
    # if request.args.get('LoginName'):
    #    request.args['loginName'] = request.args.get('LoginName')

    exampleUser = DB_User()
    exampleUser.loginName = 'some customized-user'

    #form = FormSearchLogin(obj=exampleUser)
    form = FormSearchLogin(request.args,obj=exampleUser)
    if form.validate_on_submit():
        flash('Form validated!')
        return redirect(url_for('index'))
    return render_template(
        'form.html',
        form=form
    )


if __name__ == '__main__':
    app.run(debug=True)
