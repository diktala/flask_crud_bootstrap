# -*- coding: utf-8 -*-
""" Model to access Aladin mssql

This contains functions to be called by Flask blueprints to access Aladin sql

Example:
    myResult = queryDBall('SELECT "DateJoined", LoginName FROM UsersId')
    myResultJson = json.dumps(myResult, indent = 4)
    print (myResultJson)
    pprint(myResult)
    # ex: python src/erz-quick-query.py > temp-file.txt
    #     cat temp-file.txt | jq '.'
    #     cat temp-file.txt| jq -C '. | [.[]] | .[] | ."ReferredBy" '
"""
import os
from pymssql import _mssql

DB_IP = os.environ.get("DB_IP")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")


class fake_mssql:
    def connect(server, user, password, database):
        return fake_mssql()

    def execute_query(self, query, params):
        return fake_mssql()

    def execute_scalar(self, query, params):
        return fake_mssql()

    def close(self):
        return fake_mssql()


if DB_IP is None:
    dbLink = fake_mssql.connect(
        server="",
        user="",
        password="",
        database="",
    )
else:
    dbLink = _mssql.connect(
        server=DB_IP,
        user=DB_USER,
        password=DB_PASS,
        database="wwwMaintenance",
    )


def queryDBrow(query, params=""):
    dbLink.execute_query(query, params)
    queryResult = {}
    # trick to differentiate pymssql vs fake_mssql
    if hasattr(dbLink, "__iter__"):
        for row in dbLink:
            for column in row.keys():
                if isinstance(column, str):
                    queryResult.update({column: row[column]})
            break
    dbLink.close
    return queryResult


def queryDBscalar(query, params=""):
    queryResult = dbLink.execute_scalar(query, params)
    dbLink.close
    return queryResult


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
