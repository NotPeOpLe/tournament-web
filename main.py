from flask import Flask, render_template, url_for, redirect, send_from_directory
from blueprints import tourney, api
import example, re, os

app = Flask(__name__)
app.register_blueprint(tourney, url_prefix='/manager')
app.register_blueprint(api, url_prefix='/api')

@app.route('/favicon.ico')
def faviconico():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    """
    比賽官網的首頁，中間LOGO或者公告欄、註冊報名等連結，下方放相關連結，如osu!forums、discord、sheets等
    """
    return render_template('index.html')

@app.route('/base')
def base():
    """
    testing
    """
    return render_template('base.html')

@app.route('/info/')
def info():
    """
    比賽資訊文檔
    """
    return render_template('info.html')

@app.route('/rules/')
def rules():
    """
    比賽規則文檔
    """
    return render_template('rules.html')

@app.route('/schedule/')
def schedule():
    return render_template('schedule.html')

@app.route('/matchs/<match_id>')
def matchs(match=None):
    """
    查看比賽最近的賽程，歷史紀錄
    """
    return render_template('matchs.html', match=match)

@app.route('/registeredlist/')
def registeredlist():
    """
    顯示已報名的名單
    """
    
    players = example.registered_list
    return render_template('registeredlist.html', players=players)


@app.route('/player/<user_id>')
def player(user_id=None):
    """
    顯示玩家資訊
    """
    return render_template('player.html', user=user_id)

# @app.route('/teams/')
# @app.route('/teams/<team_id>')
# def teams(team=None):
#     """
#     列出本比賽所有參賽隊伍
#     """
#     return render_template('teams.html', team=team)

@app.route('/mappools/<pool_id>')
def mappools(pool_id=None):
    """
    顯示圖譜資訊
    """
    mappool = example.mappools
    return render_template('mappools.html', mappool=mappool)

@app.route('/staff/')
def staff():
    """
    列出本比賽所有工作人員
    """
    staff = example.staff

    return render_template('staff.html', staff=staff)


@app.template_filter('num')
def num_filter(num):
    if type(num) == int:
        return f'{num:,}'
    remain_amount = '%0.2f' % (num * 100 / 100.0)
    remain_amount_format =re.sub(r"(\d)(?=(\d\d\d)+(?!\d))", r"\1,", remain_amount)
    return remain_amount_format

@app.template_filter('floatfix')
def num_filter(num):
    remain_amount = '%0.2f' % (float(num))
    remain_amount_format =re.sub(r"(\d)(?=(\d\d\d)+(?!\d))", r"\1,", remain_amount)
    return remain_amount_format

if __name__ == '__main__':
    app.run(port=80,debug=True)