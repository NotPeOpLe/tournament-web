from flask import Flask
from flask.templating import render_template
from blueprints import tourney, api

app = Flask(__name__)
app.register_blueprint(tourney, url_prefix='/manager')
app.register_blueprint(api, url_prefix='/api')

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

@app.route('/rule/')
def rule():
    """
    比賽規則文檔，使用html編寫
    """
    return render_template('rule.html')

@app.route('/matchs/')
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
    return render_template('registeredlist.html')


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

@app.route('/staff/')
def staff():
    """
    列出本比賽所有工作人員
    """
    staff = example.staff

    return render_template('staff.html', staff=staff)


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=80,
        debug=True,
    )