# -*- coding: utf-8 -*-
import os
import re
import json
from pprint import pprint
from datetime import datetime as dt
from pymssql import _mssql

DB_IP = os.environ.get("DB_IP")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
dbLink = _mssql.connect(
    server=DB_IP,
    user=DB_USER,
    password=DB_PASS,
    database="wwwMaintenance",
)


def queryDBall(query, params=""):
    dbLink.execute_query(query, params)
    lineNumber = 0
    allRows = {}
    rowResult = {}
    for row in dbLink:
        for column in row.keys():
            if isinstance(column, str):
                rowResult.update({column: row[column]})
        allRows[lineNumber] = rowResult.copy()
        lineNumber += 1
    dbLink.close
    return allRows

# myResult = queryDBall("SELECT OperatingSystem, LoginName FROM UsersId WHERE LoginName like 'tria%'")
myResult = queryDBall("SELECT DateJoined, LoginName FROM UsersId")
myResultJson = json.dumps(myResult, indent = 4)
print (myResultJson)
# pprint(myResult)


