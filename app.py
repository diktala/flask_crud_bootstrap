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


class HelloForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def test_form():
    # form = HelloForm(request.args)
    form = HelloForm()
    if form.validate_on_submit():
        flash('Form validated!')
        return redirect(url_for('index'))
    return render_template(
        'form.html',
        form=form
    )


if __name__ == '__main__':
    app.run(debug=True)
