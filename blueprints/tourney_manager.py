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
def context():
    if session == {}:
        user = None
    else:
        user = get('view_staff', str(session['id']))

    return dict(
        cur_user=user,
        rounds=db.query_all("select * from round"),
    )

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
            user = db.get_staff(user_id=session['user_id'])
            if user == None:
                return redirect(url_for('tourney.gologin'))
            user_privilege = Staff(user['privileges'])
            if privilege not in user_privilege:
                flash(f'你沒有 {privilege.name} 權限!', 'danger')
                return redirect(url_for('tourney.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_privilege(id, privilege: Staff):
    user = db.get_staff(staff_id=id)
    user_privilege = Staff(user['privileges'])
    return bool(privilege in user_privilege)

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
            sql = db.get_staff(user_id=user['id'])
            if sql:
                login(sql)
                return redirect(url_for('tourney.dashboard'))
            else:
                flash('看來你不是工作人員，請回吧')
                log.debug(user)
                return redirect(url_for('index'))
        except Exception as e:
            log.exception(e)
    return redirect(url_for('index'))


@tourney.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@tourney.route('/schedule/', methods=['GET', 'POST'])
@login_required
def matchs_job():
        mid = int(request.form['id'])
        uid = session['id']
        job = request.form['job']
        action = request.form['action']
        match = db.query_one("select * from `match` where id = %s", [mid])

        def update(id, privilege: Staff, ctx, args=None, success_msg=''):
            if check_privilege(id, privilege):
                try:
                    db.query(ctx, args)
                    flash(success_msg,'success')
                except Exception as e:
                    flash(e, 'danger')
                finally:
                    return redirect(url_for('tourney.matchs'))
            else:
                flash('你沒有 %s 權限' % privilege.name, 'danger')
                return redirect(url_for('tourney.matchs'))

        if match:
            if match['stats'] == 0:
                update_query = "Update `match` Set $x Where id = %d" % mid
                privilege = Staff.STAFF
                if action == 'get':
                    success_msg = ''
                    if job == 'ref':
                        update_query = update_query.replace('$x', 'referee = %d' % uid)
                        success_msg='你已接下場次 %d 的裁判工作' % mid
                    privilege = Staff.REFEREE
                    elif job == 'stream':
                        update_query = update_query.replace('$x', 'streamer = %d' % uid)
                        success_msg='你已接下場次 %d 的直播工作' % mid
                        privilege = Staff.STREAMER
                    elif job == 'comm':
                        if match['commentator']:
                            update_query = update_query.replace('$x', 'commentator2 = %d' % uid)
                            success_msg='你已接下場次 %d 的賽評工作' % mid
                            privilege = Staff.COMMENTATOR
                        elif match['commentator'] and match['commentator2']:
                            flash('該場次已經塞不下更多的賽評了!', 'danger')
                            return redirect(url_for('tourney.matchs'))
                        else:
                            update_query = update_query.replace('$x', 'commentator = %d' % uid)
                            success_msg='你已接下場次 %d 的賽評工作' % mid
                            privilege = Staff.COMMENTATOR
                    else:
                        flash('job的值"%s"不是有效的值' % job, 'danger')
                        return redirect(url_for('tourney.matchs'))
                    return update(uid, privilege, update_query, success_msg=success_msg)
                elif action == 'remove':
                    success_msg = ''
                    privilege = Staff.STAFF
                    if job == 'ref' and match['referee'] == uid:
                        success_msg = '你已解除場次 %d 的裁判工作' % mid
                        update_query = update_query.replace('$x', 'referee = NULL')
                    privilege = Staff.REFEREE
                    elif job == 'stream' and match['streamer'] == uid:
                        success_msg = '你已解除場次 %d 的直播工作' % mid
                        update_query = update_query.replace('$x', 'streamer = NULL')
                        privilege = Staff.STREAMER
                    elif job == 'comm':
                        if match['commentator'] == uid:
                            update_query = update_query.replace('$x', 'commentator = NULL')
                        elif match['commentator2'] == uid:
                            update_query = update_query.replace('$x', 'commentator2 = NULL')
                        success_msg = '你已解除場次 %d 的賽評工作' % mid
                        privilege = Staff.COMMENTATOR
                    else:
                        if job not in ('ref', 'stream', 'comm'):
                            flash('job 的值"%s"不是有效的值' % job, 'danger')
                            return redirect(url_for('tourney.matchs'))
                        else:
                            flash('你沒有接過該場次的工作', 'danger')
                            return redirect(url_for('tourney.matchs'))
                            
                    return update(uid, privilege, update_query, success_msg=success_msg)
                else:
                    flash('action 的值"%s"不是有效的值' % action, 'danger')
                    return redirect(url_for('tourney.matchs'))
            else:
                flash('match_id: %d 改場次已結束!' % mid, 'danger')
                return redirect(url_for('tourney.matchs'))
        else:
            flash('match_id: %d 找不到對應的場次!' % mid, 'danger')
            return redirect(url_for('tourney.matchs'))

@tourney.route('/teams/')
@login_required
def teams():
    return render_template('manager/teams.html')


@tourney.route('/staff/', methods=['GET', 'POST'])
@login_required
@need_privilege(Staff.ADMIN)
def staff():
    if request.method == 'POST':
        try:
            console.log(dict(request.form))
            postype = request.form['type']
            user_id = int(request.form['id'])
            if postype in ('add', 'update'):
                group = int(request.form['group'])
                privileges = int(request.form['privileges'])
                username = osuapi.get(osuapi.V1Path.get_user, u=user_id)[0]['username']
                if postype == 'add':
                    if db.query_one("Select user_id from staff where user_id = %s", (user_id,)) == None:
                        db.query("Insert into staff (user_id, username, group_id, privileges) Values (%s, %s, %s, %s)", (user_id, username, group, privileges))
                    else:
                        db.query("Update staff Set group_id = %s, privileges = %s, username = %s, active = 1 Where user_id = %s", (group, privileges, username, user_id))
                elif postype == 'update':
                    db.query("Update staff Set group_id = %s, privileges = %s, username = %s Where user_id = %s", (group, privileges, username, user_id))
            elif postype == 'disable':
                db.query("Update staff Set active = 0 Where user_id = %s", (user_id,))
            elif postype == 'enable':
                db.query("Update staff Set active = 1 Where user_id = %s", (user_id,))
        except Exception as e:
            flash(e.args[0], 'danger')
            log.exception(e)
        finally:
            return redirect(url_for('tourney.staff'))

    return render_template('manager/staff.html', staff=get('view_staff', '*'))


@tourney.route('/settings/', methods=['GET', 'POST'])
@login_required
@need_privilege(Staff.HOST)
def settings():
    if request.method == 'POST':
        if len(request.form):
            update_text = ''
            for k, v in request.form.items():
                if v.isdigit():
                    update_text += f"{k}={v},"
                else:
                    update_text += f"{k}='{v}',"
            
            db.query(f"UPDATE tourney SET {update_text[:-1]} WHERE id = 1")
            flash('儲存成功', 'success')
            return redirect(url_for('tourney.settings'))
    return render_template('manager/settings.html', settings=db.query_one('select * from tourney where id = 1'))


@tourney.route('/mappool/')
@tourney.route('/mappool/<round_id>', methods=['GET', 'POST'])
@login_required
@need_privilege(Staff.MAPPOOLER)
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
            if round_info['pool_publish'] == 1:
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
            # 圖譜插入至SQL
            db.query('insert into mappool (`round_id`, `beatmap_id`, `group`, `code`, `mods`, `info`, `note`, `nominator`) values (%s, %s, %s, %s, %s, %s, %s, %s)',
                (int(round_id), int(beatmap_id), group, modcount['count']+1, use_mods, json.dumps(beatmap), note, poster))
            
            # 成功訊息
            info = '%s - %s [%s] (%s) 已新增至 %s' % (beatmap['artist'], beatmap['title'], beatmap['version'], group, round_info['name'])
            flash(info, 'success')
        except Exception as e:
            # 錯誤訊息
            flash(e.args[0], 'danger')
            log.exception(e)
        finally:
            return redirect(url_for('tourney.mappool', round_id=round_id))

    # GET: 查看網頁
    mappool = db.get_mappool(round_id, ingore_pool_publish=True, format=False)
    return render_template('manager/mappool.html', round_id=round_id, mappool=mappool)