# flask-crud-bootstrap
flask with crud form and bootstrap css

---

cd ~/Desktop
mkdir ~/Desktop/flaskor; cd ~/Desktop/flaskor
python3 -m venv venv
source venv/bin/activate
git clone git@github.com:diktala/flask-crud-bootstrap.git
cd flask-crud-bootstrap

pip list
pip install --upgrade pip

# uninstall all but basics / reset pip:
pip list | grep -A 100 '\---' | grep -Ev '(\---)|(^pip)|(setuptools)' | cut -d ' ' -f 1 | sed -r 's=(.*)=yes| pip uninstall \1='

# install flask
pip install bootstrap-flask
pip install flask-sqlalchemy
pip install flask-wtf

# get example skeleton from bootstrap-flask
git clone https://github.com/greyli/bootstrap-flask.git
# git init myflask
cp -R ~/Desktop/flaskor/bootstrap-flask/examples/bootstrap5/ ~/Desktop/flaskor/flask-crud-bootstrap
cd ~/Desktop/flaskor/flask-crud-bootstrap/
python ./app.py

# initial fixes
 # pagination = Message.query.paginate(page, per_page=10)
 pagination = Message.query.paginate(per_page=10)

 # serve locally
 app.config['BOOTSTRAP_SERVE_LOCAL'] = True

------------------

