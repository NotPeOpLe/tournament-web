from flask import Flask
from flask.templating import render_template
from blueprints import tourney, api

app = Flask(__name__)
app.register_blueprint(tourney, url_prefix='/staff')
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    """
    比賽官網的首頁，中間LOGO或者公告欄、註冊報名等連結，下方放相關連結，如osu!forums、discord、sheets等
    """
    return render_template('index.html')

@app.route('/rule')
def rule():
    """
    比賽規則文檔，使用html編寫
    """
    return render_template('rule.html')

@app.route('/matchs')
def matchs():
    """
    查看比賽最近的賽程，歷史紀錄
    """
    return render_template('matchs.html')

@app.route('/matchs/<match_id>')
def view_match(match_id):
    """
    查看比賽最近的賽程，歷史紀錄
    """
    match = get_match(match_id)
    return render_template('matchs.html', match=match_id)

@app.route('/teams')
def teams():
    """
    列出本比賽所有參賽隊伍
    """
    return render_template('teams.html')

@app.route('/teams/<team_id>')
def view_team(team_id):
    """
    查看目標隊伍的詳細內容
    """
    team = get_team(team_id)
    return render_template('team.html', team=team)

@app.route('/staff')
def staff():
    """
    列出本比賽所有工作人員
    """
    return render_template('staff.html')


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=80,
        debug=True,
    )