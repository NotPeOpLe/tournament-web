from config import Config
from functools import wraps
from types import resolve_bases
from flask import Blueprint, render_template, jsonify, Response, abort, session, request, redirect, url_for
from werkzeug.exceptions import HTTPException
from pymysql.err import *
import mysql, json, requests

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
        return db.query("SELECT COUNT(*) as match_count, r.pool_publish from `match` lnner join `round` as r on r.id=round_id WHERE round_id = %s", (request.args.get('id'),))
    else:
        abort(400, 'id?')

@api.route('/teams/<int:team_id>/')
@login_required
def teams(team_id: int):
    try:
        data = db.query_one("SELECT json FROM `json_team` WHERE id = %s", (team_id,))
        return jsonify(json.loads(data['json']))
    except Exception as e:
        abort(400, e)

@api.route('/maps/<int:map_id>/')
@login_required
def maps(map_id: int):
    try:
        data = db.query_one("SELECT json FROM `json_mappool` WHERE id = %s", (map_id,))
        return jsonify(json.loads(data['json']))
    except Exception as e:
        abort(400, e)

@api.route('/web/<p>')
@login_required
def osuapiv1(p):
    try:
        args = request.args.to_dict()
        args['k'] = Config.OSU_API_KEY
        req = requests.get(
            url = 'https://osu.ppy.sh/api/%s' % p,
            params = args
            )

        result = req.json()
        if len(result):
            return jsonify(result)
        else:
            return 'no context', 400
    except Exception as e:
        abort(400, e)

@api.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(error=str(e)), HTTPException.code
