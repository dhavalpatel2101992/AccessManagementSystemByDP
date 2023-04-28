from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import AD_User, AD_Team
import json
from sqlalchemy import and_,or_

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_count = AD_User.query.count()
    team_count = AD_Team.query.count()
    team_list = AD_Team.query.all()
    return render_template("home.html", user=current_user,user_count=user_count,team_count=team_count)

@views.route('/add-team', methods=['GET', 'POST'])
@login_required
def add_team():
    if request.method == 'POST':
        email = request.form.get('email')
        teamname = request.form.get('teamname')
        tribename = request.form.get('tribename')

        db_teamname = AD_Team.query.filter_by(name=teamname).first()
        db_email = AD_Team.query.filter_by(email=email).first()
        if db_teamname:
            flash('Name already exists.', category='error')
        elif db_email:
            flash('Email ID already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(teamname) < 2:
            flash('Team name must be greater than 1 character.', category='error')
        elif len(tribename) < 2:
            flash('Tribe name must be greater than 1 character.', category='error')
        else:
            new_team = AD_Team(email=email, name=teamname, tribename=tribename)
            db.session.add(new_team)
            db.session.commit()
            flash('Team ({0}) created!'.format(teamname), category='success')
            return redirect(url_for('views.teampage'))

    return render_template('add_team.html', user=current_user)

@views.route('/update-team/<int:team_id>', methods=['GET','POST'])
@login_required
def update_team(team_id):
    if request.method == 'POST':
        id = request.form.get('teamid')
        email = request.form.get('email')
        teamname = request.form.get('teamname')
        tribename = request.form.get('tribename')

        db_teamname = AD_Team.query.filter(and_(AD_Team.name==teamname,AD_Team.id != id)).first()
        db_email = AD_Team.query.filter(and_(AD_Team.email==email,AD_Team.id != id)).first()
        if db_teamname:
            flash('Name already exists.', category='error')
        elif db_email:
            flash('Email ID already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(teamname) < 2:
            flash('Team name must be greater than 1 character.', category='error')
        elif len(tribename) < 2:
            flash('Tribe name must be greater than 1 character.', category='error')
        else:
            AD_Team.query.filter_by(id=id).update({'name': teamname, 'email': email, 'tribename': tribename})
            db.session.commit()
            flash('Team ({0}) updated !'.format(teamname), category='success')
            return redirect(url_for('views.teampage'))
    db_team = AD_Team.query.get_or_404(team_id)
    return render_template('update_team.html', team=db_team, user=current_user)

@views.route('/delete-team/<int:team_id>', methods=['GET','POST'])
@login_required
def delete_team(team_id):
    db_team = AD_Team.query.get_or_404(team_id)

    if request.method == 'POST':
        db.session.delete(db_team)
        db.session.commit()
        flash('Team ({0}) deleted !'.format(db_team.name), category='success')
        return redirect(url_for('views.teampage'))

    return render_template('delete_team.html', team=db_team, user=current_user)

@views.route('/userpage', methods=['GET'])
@login_required
def userpage():
    user_list = AD_User.query.all()
    return render_template("userpage.html", user=current_user, user_list=user_list)

@views.route('/teampage', methods=['GET'])
@login_required
def teampage():
    team_list = AD_Team.query.all()
    return render_template("teampage.html", user=current_user, team_list=team_list)


@views.route('/ldapsynch', methods=['GET'])
@login_required
def ldapsynch():
    with open('website/userdata.json', 'r') as openfile:
        user_list = json.load(openfile)
    user_entries = []
    for useritem in user_list:
        user = AD_User.query.filter_by(email=useritem['email']).first()
        if user:
            pass
        else:
            user_entries.append(AD_User(name=useritem['name'], email=useritem['email'], corpkey=useritem['corpkey']))
    db.session.add_all(user_entries)
    db.session.commit()
    flash('{0} Users have been added from LDAP!'.format(len(user_entries)), category='success')
    return redirect(url_for('views.userpage'))

@views.route('/team/<int:team_id>/assign-users', methods=['GET', 'POST'])
@login_required
def team_assign_users(team_id):
    team = AD_Team.query.get_or_404(team_id)

    if request.method == 'POST':
        assigned_user_ids = request.form.getlist('assigned_user_ids')
        remaining_user_ids = request.form.getlist('remaining_user_ids')
        assigned_users = AD_User.query.filter(and_(AD_User.id.in_(assigned_user_ids), or_(~AD_User.teams.any(AD_Team.id == team_id),AD_User.teams == None))).all()
        remaining_users = AD_User.query.filter(AD_User.id.in_(remaining_user_ids), AD_User.teams.any(AD_Team.id == team_id)).all()

        for user in assigned_users:
            user.teams.append(team)
        for user in remaining_users:
            user.teams.remove(team)
        db.session.commit()
        flash('{0} Users have been added and {1} Users have been removed from team {2}'.format(len(assigned_users), len(remaining_users), team.name), category='success')
        return redirect(url_for('views.teampage'))

    assigned_users = team.users
    remaining_users = AD_User.query.filter(~AD_User.teams.any(AD_Team.id == team_id)).all()

    return render_template('team_assign_users.html', team=team, user=current_user,assigned_users=assigned_users, remaining_users=remaining_users)

@views.route('/user/<int:user_id>/assign-teams', methods=['GET', 'POST'])
@login_required
def user_assign_teams(user_id):
    db_user = AD_User.query.get_or_404(user_id)

    if request.method == 'POST':
        assigned_team_ids = request.form.getlist('assigned_team_ids')
        remaining_team_ids = request.form.getlist('remaining_team_ids')
        assigned_teams = AD_Team.query.filter(and_(AD_Team.id.in_(assigned_team_ids), or_(~AD_Team.users.any(AD_User.id == user_id),AD_Team.users == None))).all()
        remaining_teams = AD_Team.query.filter(AD_Team.id.in_(remaining_team_ids), AD_Team.users.any(AD_User.id == user_id)).all()

        for team in assigned_teams:
            team.users.append(db_user)
        for team in remaining_teams:
            team.users.remove(db_user)
        db.session.commit()
        flash('{0} Teams have been added and {1} Teams have been removed from user {2}'.format(len(assigned_teams), len(remaining_teams), db_user.name), category='success')
        return redirect(url_for('views.userpage'))

    assigned_teams = db_user.teams
    remaining_teams = AD_Team.query.filter(~AD_Team.users.any(AD_User.id == user_id)).all()

    return render_template('user_assign_teams.html', db_user=db_user, user=current_user,assigned_teams=assigned_teams, remaining_teams=remaining_teams)

@views.route('/view-team/<int:team_id>', methods=['GET','POST'])
@login_required
def view_team(team_id):
    db_team = AD_Team.query.get(team_id)
    return render_template('view_team.html', team=db_team, user=current_user)

@views.route('/view-user/<int:user_id>', methods=['GET','POST'])
@login_required
def view_user(user_id):
    db_user = AD_User.query.get(user_id)
    return render_template('view_user.html', db_user=db_user, user=current_user)