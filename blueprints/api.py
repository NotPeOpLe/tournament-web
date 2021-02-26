from functools import wraps
from types import resolve_bases
from flask import Blueprint, render_template, jsonify, Response, abort, session, redirect, url_for
from flask.globals import request
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session == {}:
            abort(400, 'no session')
        return f(*args, **kwargs)
    return decorated_function

@api.route('/show/<table_name>')
@login_required
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

@api.route('/data/<table_name>/<id>')
@login_required
def getdata(table_name:str, id:str):
    if table_name in ('game', 'group', 'map_group', 'mappool', 'match', 'player', 'round', 'staff', 'team', 'tourney', 'view_staff'):
        if id.isdigit():
            return jsonify(data=db.query_one('select * from `%s` where id = %s limit 1' % (table_name, id)))
        elif id == '*':
            return jsonify(data=db.query_all('select * from `%s`' % table_name))
        else:
            abort(404)
    else:
        abort(404)
        
@api.route('/check_round')
def check_round():
    if request.args.get('id'):
        return db.query("SELECT COUNT(*) as match_count from `match` WHERE round_id = %s", (request.args.get('id'),))
    else:
        abort(400, 'id?')

@api.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(error=str(e)), HTTPException.code