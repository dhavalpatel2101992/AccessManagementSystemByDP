from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

AD_UserTeam = db.Table('ad_userteam',
    db.Column('user_id',db.Integer, db.ForeignKey('ad_user.id'), primary_key=True),
    db.Column('team_id',db.Integer, db.ForeignKey('ad_team.id'), primary_key=True),
    db.Column('create_date', db.DateTime(timezone=True), default=func.now())
    )

class AD_User(db.Model):
    __tablename__ = 'ad_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    corpkey = db.Column(db.String(6))
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    #teams = db.relationship('AD_Team', secondary=AD_UserTeam, backref ='user')
    teams = db.relationship('AD_Team', secondary=AD_UserTeam, back_populates ='users')

class AD_Team(db.Model):
    __tablename__ = 'ad_team'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150), unique=True)
    tribename = db.Column(db.String(150))
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    #users = db.relationship('AD_User', secondary=AD_UserTeam, backref='team')
    users = db.relationship('AD_User', secondary=AD_UserTeam, back_populates='teams')