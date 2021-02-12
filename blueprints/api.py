from types import resolve_bases
from flask import Blueprint, json, render_template, jsonify, Response, abort
from werkzeug.exceptions import HTTPException
from pymysql.err import *
import mysql

db = mysql.DB()
api = Blueprint('api', __name__)

funs = {
    'get_mappool': db.get_mappool,
    'get_teams': db.get_teams,
    'get_players': db.get_players,
    'get_matchs': db.get_matchs,
    'get_staff': db.get_staff,
}

@api.route('/show/<table_name>')
def show_data(table_name):
    def sql():
        try:
            return db.query_all("SELECT * FROM `%s`;" % table_name)
        except Exception:
            abort(404)

    if table_name == '*':
        return jsonify(db.query_all("SHOW TABLE STATUS FROM `tourney`;"))
    elif table_name in funs.keys():
        return jsonify(funs.get(table_name, sql)())
    else:
        abort(404)
    
    

@api.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(error=str(e)), HTTPException.code