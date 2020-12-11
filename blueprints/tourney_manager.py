from flask import Blueprint, render_template

tourney = Blueprint('tourney', __name__)

@tourney.route('/')
def dashboard():
    return render_template('tourney/dashboard.html')

@tourney.route('/matchs')
def matchs():
    return render_template('tourney/matchs.html')

@tourney.route('/teams')
def teams():
    return render_template('tourney/teams.html')

@tourney.route('/staff')
def staff():
    return render_template('tourney/staff.html')

@tourney.route('/settings')
def settings():
    return render_template('tourney/settings.html')