# flask_crud_bootstrap
flask with crud form and bootstrap css

---

#### setup venv
```
cd ~/Desktop
mkdir ~/Desktop/flaskor; cd ~/Desktop/flaskor
python3 -m venv venv
source venv/bin/activate
git clone git@github.com:diktala/flask_crud_bootstrap.git
cd flask_crud_bootstrap
pip list
pip install --upgrade pip

pip install pymssql
pip install bootstrap-flask
pip install flask-sqlalchemy
pip install flask-wtf
pip install black djlint

python ./app.py
```

---

#### another session of venv
```
cd ~/Desktop/
python3 -m venv ~/Desktop/flaskor/venv
source ~/Desktop/flaskor/venv/bin/activate
cd ~/Desktop/flaskor/flask_crud_bootstrap
```

---

#### uninstall all but basics / reset pip:
```
pip list | grep -A 100 '\---' | grep -Ev '(\---)|(^pip)|(setuptools)' | cut -d ' ' -f 1 | sed -r 's=(.*)=yes| pip uninstall \1='
```

---

#### formatters:
```
djlint --reformat --format-css --format-js *.html
black *.py
```

---

#### example sqlalchemy raw sql:
```
db.session.execute('select "123" as "a", "333" as "b", "000" as "c"').columns(2).scalar()
> > >  000
```
```
users = db.session.execute('select * from UsersId')
users.fetchone()
```

---

#### OPTION: sqlalchemy+pymssql
```
#!/usr/bin/env python3

# max version:
# pip install sqlalchemy==1.3.24
# pip install pymssql
# pip install flask-sqlalchemy==2.5.0

# from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
# engine = create_engine(F"mssql+pymssql://{DB_USER}:{DB_PASS}@{DB_IP}/wwwMaintenance")
# meta = MetaData()
# taxes = Table( taxes, meta, Column('TaxCode', String, primary_key = True))
# s = taxes.select()
# conn = engine.connect()
# result = conn.execute(s)
# for row in result: print(row)
```

---

#### OPTION pymssql
```
from pymssql import _mssql
dbLink = _mssql.connect(server=F"{DB_IP}", user=F"{DB_USER}", password=F"{DB_PASS}", database="wwwMaintenance")
dbLink.execute_query("SELECT * from taxes")

for row in dbLink:
    print(F"row {row['TaxCode']}")
dbLink.close
```
