from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from logger import log
from flag import Staff, Mods
from rich.console import Console
from functools import wraps
import osuapi, mysql, json

tourney = Blueprint('tourney', __name__)
db = mysql.DB()
console = Console()

@tourney.context_processor
def rounds():
    return dict(rounds=db.query_all("select * from round"))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        console.log(dict(session))
        if session == {}:
            return redirect(url_for('tourney.gologin'))
        return f(*args, **kwargs)
    return decorated_function


def need_privilege(privilege: Staff):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = db.get_staff(session['user_id'])
            user_privilege = Staff(user['privileges'])
            if privilege not in user_privilege:
                flash(f'你沒有 {privilege.name} 權限!', 'danger')
                return redirect(url_for('tourney.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@tourney.route('/')
@login_required
def dashboard():
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


@tourney.route('/matchs/')
@login_required
def matchs():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/matchs.html')


@tourney.route('/teams/')
@login_required
def teams():
    if session == {}: return redirect(url_for('tourney.gologin'))
    return render_template('manager/teams.html')


@tourney.route('/staff/')
@login_required
@need_privilege(Staff.ADMIN)
def staff():

    return render_template('manager/staff.html', staff=db.get_staff(format=False))


@tourney.route('/settings')
@login_required
def settings():
    return render_template('manager/settings.html')


@tourney.route('/mappool/')
@tourney.route('/mappool/<round_id>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
@login_required
@need_privilege((Staff.MAPPOOLER))
def mappool(round_id=None):
    if round_id == None: return redirect(url_for('tourney.mappool', round_id=1))
    
    # POST: 新增圖譜
    if request.method == 'POST':
        try:
            # request.form 取得的訊息
            beatmap_id:str = request.form['id']      # 圖譜Id
            if not beatmap_id.isdigit(): 
                raise ValueError('beatmap_id 必須是數字')
            use_mods = request.form['mods']      # 開啟的Mods
            group = request.form['group']        # 分類
            note = request.form['note']          # 備註

            # session 取得的訊息
            poster = int(session['id'])          # 提名人Id

            # sql 取得的訊息
            round_info = db.query_one('select * from round where id = %s', (round_id,)) # Round 資料
            if not round_info['pool_publish']:
                raise Exception('此階段圖池已公布，無法進行變動!')
            modcount = db.query_one('SELECT `group`, COUNT(*) AS `count` FROM mappool WHERE round_id = 1 and `group` = %s', (request.form['group'],)) # 取得該 group 計數

            
            # 判斷是否為會改變難度的mods
            if use_mods in ('tb', 'fm') :
                request_mods = 0
            elif Mods(int(use_mods)) in (Mods.Easy | Mods.HalfTime | Mods.HardRock | Mods.DoubleTime | Mods.Nightcore):
                request_mods = use_mods
            else : 
                request_mods = 0

            # api 取得的訊息
            beatmap = osuapi.get(osuapi.V1Path.get_beatmaps, b=request.form['id'], m=0, mods=request_mods)[0]
            # 將 api 的資料轉換成正確的類型
            for k in beatmap:
                beatmap[k] = osuapi.todata(beatmap[k])

            # debug
            log.debug(dict(request.form))
            console.log('', log_locals=True)
            # 圖譜插入至SQL
            db.query('insert into mappool (`round_id`, `beatmap_id`, `group`, `code`, `mods`, `info`, `note`, `nominator`) values (%s, %s, %s, %s, %s, %s, %s, %s)',
                (int(round_id), int(beatmap_id), group, modcount['count']+1, use_mods, json.dumps(beatmap), note, poster))
            
            # 成功訊息
            info = '%s - %s [%s] (%s) 已新增至 %s' % (beatmap['artist'], beatmap['title'], beatmap['version'], group, round_info['name'])
            flash(info, 'success')
        except Exception as e:
            # 錯誤訊息
            flash(e.args, 'danger')
            log.exception(e)
        finally:
            return redirect(url_for('tourney.mappool', round_id=round_id))

    # GET: 查看網頁
    mappool = db.get_mappool(round_id, ingore_pool_publish=True, format=False)
    return render_template('manager/mappool.html', round_id=round_id, mappool=mappool)