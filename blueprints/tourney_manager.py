from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from logger import log
from flag import StaffPrivilege, Mods
import osuapi, mysql, json

tourney = Blueprint('tourney', __name__)
db = mysql.DB()

@tourney.context_processor
def rounds():
    return dict(rounds=db.query_all("select * from round"))

@tourney.route('/')
def dashboard():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/dashboard.html')

@tourney.route('/login')
def gologin():
    return render_template('manager/auth.html')

def login(user):
    session.clear()
    session.permanent = True
    session['id'] = user['id']
    session['user_id'] = user['user_id']
    session['username'] = user['username']

@tourney.route('/callback')
def callback():
    if request.args.get('state') == 'login':
        u = osuapi.get_token(request.args['code'])
        try:
            user = osuapi.get2(u['access_token'], me='')
            sql = db.get_staff(user['id'])
            if user['id'] == sql['user_id']:
                login(sql)
                return redirect(url_for('tourney.dashboard'))
        except Exception as e:
            log.debug(locals())
            log.exception(e)
    return redirect(url_for('index'))

@tourney.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@tourney.route('/matchs')
def matchs():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/matchs.html')

@tourney.route('/teams')
def teams():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/teams.html')

@tourney.route('/staff')
def staff():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/staff.html')

@tourney.route('/settings')
def settings():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/settings.html')

@tourney.route('/mappool/')
@tourney.route('/mappool/<round_id>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def mappool(round_id=None):
    if session == {}: return redirect(url_for('tourney.gologin'))
    if round_id == None: return redirect(url_for('tourney.mappool', round_id=1))

    log.debug(session)
    user = db.get_staff(session['user_id'])
    if StaffPrivilege.MAPPOOLER not in StaffPrivilege(user['privileges']):
        flash('沒有權限!', 'danger')
        return redirect(url_for('tourney.dashboard'))
    
    if request.method == 'POST':
        try:
            round_info = db.query_one('select * from round where id = %s', (round_id,))
            modcount = db.query_one('SELECT `group`, COUNT(*) AS `count` FROM mappool WHERE round_id = 1 and `group` = %s', (request.form['group'],))
            beatmap = osuapi.get(osuapi.V1Path.get_beatmaps, b=request.form['id'], m=0)[0]
            beatmap_id = int(request.form['id'])
            use_mods = int(request.form['mods'])
            group = request.form['group']
            note = request.form['note']
            poster = int(session['id'])
            for k in beatmap:
                beatmap[k] = osuapi.todata(beatmap[k])
            json_beatmap = json.dumps(beatmap)
            log.debug(dict(request.form))
            db.query('insert into mappool (`round_id`, `beatmap_id`, `group`, `code`, `mods`, `info`, `note`, `nominator`) values (%s, %s, %s, %s, %s, %s, %s, %s)',
                (int(round_id), beatmap_id, group, modcount['count']+1, use_mods, json_beatmap, note, poster))
            info = '%s - %s [%s] (%s) 已新增至 %s' % (beatmap['artist'], beatmap['title'], beatmap['version'], group, round_info['name'])
            flash(info, 'success')
        except Exception as e:
            flash(e, 'danger')
            log.exception()
        finally:
            return redirect(url_for('tourney.mappool', round_id=round_id))

    mappool = db.get_mappool(round_id, ingore_pool_publish=True, format=False)
    return render_template('manager/mappool.html', round_id=round_id, mappool=mappool)