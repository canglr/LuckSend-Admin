import hashlib
import smtplib
import uuid
import urllib
import random
from email._header_value_parser import Header
from email.mime.text import MIMEText
from time import time
from urllib.parse import urlparse

import psutil as psutil
import shortuuid as shortuuid
from cryptography.fernet import Fernet
from flask import Flask, render_template, jsonify, request, url_for, json, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


app = Flask(__name__)
POSTGRES = {
    'user': 'lucksend',
    'pw': 'XD9pLYDxaqZHlJaBVSum6uWIyC4Q1Dob',
    'db': 'Raffles',
    'host': '127.0.0.1',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SECRET_KEY'] = "6aW9HNLt7IncD6PDwo4Q9C0eUBKnXO1W"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "6aW9HNLt7IncD6PDwo4Q9C0eUBKnXO1W"

client = MongoClient('mongodb+srv://lucksend:sXu2x4z6@lucksend-echos.mongodb.net/admin?retryWrites=true&w=majority')
mongodb = client['lucksend']
InstagramProfile = mongodb['InstagramProfile']
UserKeytoId = mongodb['UserKeytoId']
SocialMedia = mongodb['SocialMedia']


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail_adress = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, nullable=False)
    local = db.Column(db.String, nullable=False)
    provider_name = db.Column(db.String, nullable=False)
    provider_id = db.Column(db.String, nullable=False)
    id_share = db.Column(db.String, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    raffleslerf = db.relationship('Raffles', backref='users', lazy=True)
    feedbacksf = db.relationship('Feedbacks', backref='users', lazy=True)
    participantsf = db.relationship('Participants', backref='users', lazy=True)
    keysf = db.relationship('Keys', backref='users', lazy=True)
    luckysf = db.relationship('Luckys', backref='users', lazy=True)
    qrcodesf = db.relationship('Qrcode', backref='users', lazy=True)
    socialstatisticssf = db.relationship('Socialstatistics', backref='users', lazy=True)
    socialsavedf = db.relationship('Socialsaved', backref='users', lazy=True)
    socialreportssf = db.relationship('Socialreports', backref='users', lazy=True)


class Raffles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_share = db.Column(db.String, nullable=False,unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    title = db.Column(db.String, nullable=False)
    contact_information = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    processing = db.Column(db.Boolean, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    delete = db.Column(db.Boolean, nullable=False)
    disable = db.Column(db.Boolean, nullable=False)
    winners = db.Column(db.Integer, nullable=False)
    reserves = db.Column(db.Integer, nullable=False)
    raffle_date = db.Column(db.DateTime, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    luckysf = db.relationship('Luckys', backref='raffles', lazy=True)
    tagstargetf = db.relationship('Tagtargets', backref='raffles', lazy=True)
    countrytargetf = db.relationship('Countrytargets', backref='raffles', lazy=True)


class Feedbacks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    description = db.Column(db.String, nullable=False)
    read = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)


class Participants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    raffle_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)


class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    key = db.Column(db.String, nullable=False)
    device_key = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    device_information_id = db.Column(db.Integer, db.ForeignKey('deviceinformation.id'),nullable=False)


class Luckys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    raffles_id = db.Column(db.Integer, db.ForeignKey('raffles.id'),nullable=False)
    secret_key = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.Boolean, nullable=False)
    check_key = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)


class Deviceinformation(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    brand = db.Column(db.String,nullable=False)
    model = db.Column(db.String,nullable=False)
    release = db.Column(db.String,nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    keysf = db.relationship('Keys', backref='deviceinformation', lazy=True)


class Tags(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tag_name = db.Column(db.String,nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    tagsf = db.relationship('Tagtargets', backref='tags', lazy=True)


class Tagtargets(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'),nullable=False)
    raffle_id = db.Column(db.Integer, db.ForeignKey('raffles.id'),nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)


class Countries(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    country_code = db.Column(db.String, nullable=False)
    Countriesf = db.relationship('Countrytargets', backref='countries', lazy=True)


class Countrytargets(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    raffle_id = db.Column(db.Integer, db.ForeignKey('raffles.id'), nullable=False)


class Countrymultilang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    multi_code = db.Column(db.String, nullable=True)
    country_code = db.Column(db.String, nullable=False)
    country_name = db.Column(db.String, nullable=False)


class Versions(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    versions_name = db.Column(db.String,nullable=False)
    versions_description = db.Column(db.String,nullable=True)
    versions_code = db.Column(db.String,nullable=False)
    versions_secret_key = db.Column(db.String,nullable=False)
    contact_secret_key = db.Column(db.String,nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)


class Logs(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String, nullable=False)
    action = db.Column(db.String,nullable=False)
    data = db.Column(db.JSON,nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False)


class Qrcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)


class Socialmedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_share = db.Column(db.String, nullable=False, unique=True)
    author_name = db.Column(db.String, nullable=False)
    media_id = db.Column(db.String, nullable=False)
    media_description = db.Column(db.String, nullable=False)
    media_image = db.Column(db.String, nullable=False)
    media_url = db.Column(db.String, nullable=False)
    provider_name = db.Column(db.String,nullable=False)
    delete = db.Column(db.Boolean, nullable=False)
    disable = db.Column(db.Boolean, nullable=False)
    verification = db.Column(db.Boolean, nullable=False)
    sponsor = db.Column(db.Boolean,nullable=False)
    type = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    socialtagtargetsf = db.relationship('Socialtagtargets', backref='socialmedia', lazy=True)
    socialsavedf = db.relationship('Socialsaved', backref='socialmedia', lazy=True)
    socialstatisticsf = db.relationship('Socialstatistics', backref='socialmedia', lazy=True)
    socialcountrytargetsf = db.relationship('Socialcountrytargets', backref='socialmedia', lazy=True)
    socialreportsf = db.relationship('Socialreports', backref='socialmedia', lazy=True)


class Socialtagtargets(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    social_id = db.Column(db.Integer, db.ForeignKey('socialmedia.id'), nullable=False)


class Socialcountrytargets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    social_id = db.Column(db.Integer, db.ForeignKey('socialmedia.id'), nullable=False)


class Socialstatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    social_id = db.Column(db.Integer, db.ForeignKey('socialmedia.id'), nullable=False)
    clicks = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)


class Socialsaved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    social_id = db.Column(db.Integer, db.ForeignKey('socialmedia.id'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)


class Socialreports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    social_id = db.Column(db.Integer, db.ForeignKey('socialmedia.id'), nullable=False)
    description = db.Column(db.String, nullable=False)
    read = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)


class AdminUsers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    user_name = db.Column(db.String,nullable=False,unique=True)
    mail_address = db.Column(db.String,nullable=False,unique=True)
    password_hash = db.Column(db.String,nullable=False)
    master = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean,nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_activex(self):  # line 37
        return self.is_active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


def add_tags(tags,raffle_id):
    tagtarget_count = Tagtargets.query.filter_by(raffle_id=raffle_id).count()
    if tagtarget_count is not 0:
        db.session.query(Tagtargets).filter_by(raffle_id=raffle_id).delete()

    for tag in tags:
        tag_check = Tags.query.filter_by(tag_name=tag).first()
        if tag_check is not None:
            add_tagtarget = Tagtargets()
            add_tagtarget.tag_id = tag_check.id
            add_tagtarget.raffle_id = raffle_id
            add_tagtarget.creation_date = datetime.utcnow()
            db.session.add(add_tagtarget)
            db.session.commit()
        else:
            add_tag = Tags()
            add_tag.tag_name = tag
            add_tag.creation_date = datetime.utcnow()
            db.session.add(add_tag)
            db.session.commit()

            add_tagtarget = Tagtargets()
            add_tagtarget.tag_id = add_tag.id
            add_tagtarget.raffle_id = raffle_id
            add_tagtarget.creation_date = datetime.utcnow()
            db.session.add(add_tagtarget)
            db.session.commit()

    return None


def add_countries(countries,raffle_id):
    db.session.query(Countrytargets).filter_by(raffle_id=raffle_id).delete()
    if len(countries) is not 1:
        try:
            countries.remove("ALL")
            pass
        except ValueError:
            pass

    for country in countries:
        country_info = Countries.query.filter_by(country_code=country).first()
        add_country = Countrytargets()
        add_country.country_id = country_info.id
        add_country.raffle_id = raffle_id
        db.session.add(add_country)
        db.session.commit()
        print(country)
    return None


def aes_key_generator():
    key = Fernet.generate_key().decode(encoding="utf-8")
    return key


def md5(string):
    hash_md5 = hashlib.md5(str(string).encode('utf-8')).hexdigest()
    return hash_md5


def send_mail(mail_address,title,text):
    try:
        msg = MIMEText(str(text))
        msg['Subject'] = title
        msg['From'] = str(Header('Luck Send <no-reply@lucksend.com>'))
        msg['To'] = str(Header('<'+mail_address+'>'))
        server = smtplib.SMTP_SSL('smtp.yandex.com.tr:465')
        server.login("no-reply@lucksend.com", "MhfXJdk3WN6")
        server.sendmail('no-reply@lucksend.com', mail_address, msg.as_string())
        server.quit()
        print("Successfully sent email")
    except smtplib.SMTPException as e:
        print(e)


def stringtobool(data):
    if data == 'true':
        return True
    else:
        return False


@login_manager.user_loader
def get_user(ident):
    return AdminUsers.query.filter_by(is_active=True, id=ident).first()


@app.template_filter('datetime_short')
def _jinja2_filter_datetime(date):
    result = datetime.strftime(date, ' %Y-%m-%d %H:%M:%S')
    return result


@app.template_filter('md5')
def _jinja2_filter_md5(string):
    result = md5(string)
    return result


def cache_expiration(hours):
    date = datetime.utcnow() + relativedelta(hours=+hours)
    return date


def instagram_profile_image(user_name):
    image_check = InstagramProfile.find_one({"author_name": user_name})
    if image_check is not None:
        return image_check['author_image']
    else:
        try:
            with urllib.request.urlopen("https://www.instagram.com/" + user_name + "/") as url:
                data = url.read()
                html = BeautifulSoup(data, 'html.parser')
                image = html.find('meta', property="og:image")
                InstagramProfile.insert_one({"author_name": user_name, "author_image": image['content'],
                                             "cache_expiration": cache_expiration(12)})
            return image["content"]
        except:
            return "00"


def add_social_tags(tags,social_id):
    tagtarget_count = Socialtagtargets.query.filter_by(social_id=social_id).count()
    if tagtarget_count is not 0:
        db.session.query(Socialtagtargets).filter_by(social_id=social_id).delete()

    for tag in tags:
        tag_check = Tags.query.filter_by(tag_name=tag.strip()).first()
        if tag_check is not None:
            add_tagtarget = Socialtagtargets()
            add_tagtarget.tag_id = tag_check.id
            add_tagtarget.social_id = social_id
            db.session.add(add_tagtarget)
            db.session.commit()
        else:
            add_tag = Tags()
            add_tag.tag_name = tag.strip()
            add_tag.creation_date = datetime.utcnow()
            db.session.add(add_tag)
            db.session.commit()

            add_tagtarget = Socialtagtargets()
            add_tagtarget.tag_id = add_tag.id
            add_tagtarget.social_id = social_id
            db.session.add(add_tagtarget)
            db.session.commit()


def add_social_countries(countries,social_id):
    db.session.query(Socialcountrytargets).filter_by(social_id=social_id).delete()
    if len(countries) is not 1:
        try:
            countries.remove("ALL")
            pass
        except ValueError:
            pass

    for country in countries:
        country_info = Countries.query.filter_by(country_code=country.strip()).first()
        add_country = Socialcountrytargets()
        add_country.country_id = country_info.id
        add_country.social_id = social_id
        db.session.add(add_country)
        db.session.commit()


def uuid_short():
    rnd = random.randint(0, 2)
    if rnd == 0:
        result = shortuuid.ShortUUID().random(length=8)
    elif rnd == 1:
        result = shortuuid.ShortUUID().random(length=10)
    elif rnd == 2:
        result = shortuuid.ShortUUID().random(length=12)
    return result


@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/dashboard/app/status', methods=['POST'])
@login_required
def dashboard_app_status():
    users_count = Users.query.count()
    raffles_count = Raffles.query.count()
    raffles_completed_count = Raffles.query.filter_by(completed=True).count()
    feedbacks_count = Feedbacks.query.count()
    return jsonify(users_count=users_count,raffles_count=raffles_count,raffles_completed_count=raffles_completed_count,feedbacks_count=feedbacks_count)


@app.route('/dashboard/system/status', methods=['POST'])
@login_required
def dashboard_system_status():
    cpu = psutil.cpu_percent(interval=1)
    ram_total = psutil.virtual_memory().total >> 20
    ram_cached = psutil.virtual_memory().cached >> 20
    ram_used = psutil.virtual_memory().used >> 20
    ram_free = psutil.virtual_memory().free >> 20
    ram_swap_total = psutil.swap_memory().total >> 20
    ram_swap_used = psutil.swap_memory().used >> 20
    ram_swap_free = psutil.swap_memory().free >> 20
    uptime = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")
    d1 = datetime.strptime(uptime, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    uptime = (d2 - d1).days
    return jsonify(cpu=cpu,ram_total=ram_total,ram_cached=ram_cached,ram_used=ram_used,ram_free=ram_free,ram_swap_total=ram_swap_total,ram_swap_used=ram_swap_used,ram_swap_free=ram_swap_free,uptime=uptime)


@app.route('/Users')
@login_required
def users_list():
    page = request.args.get('page', 1, type=int)
    users = db.session.query(Users.id,Users.id_share,Users.name,Users.mail_adress).order_by(desc(Users.id)).paginate(page, 15, False)
    next_url = url_for('users_list', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('users_list', page=users.prev_num) \
        if users.has_prev else None
    return render_template('users.html', users=users, next_url=next_url, prev_url=prev_url)


@app.route('/User/detail')
@login_required
def user_detail():
    id_share = request.args.get('id', 1)
    user = Users.query.filter_by(id_share=id_share).first()
    raffles_count = Raffles.query.filter_by(user_id=user.id).count()
    participants_count = Participants.query.filter_by(user_id=user.id).count()
    devices_count = Keys.query.filter_by(user_id=user.id).count()
    feedbacks_count = Feedbacks.query.filter_by(user_id=user.id).count()
    logs_count = Logs.query.filter_by(user_id=user.id).count()
    page = request.args.get('page', 1, type=int)
    raffles = db.session.query(Raffles).filter_by(user_id=user.id).order_by(desc(Raffles.id)).paginate(
        page, 15, False)
    next_url = url_for('user_detail', page=raffles.next_num) \
        if raffles.has_next else None
    prev_url = url_for('user_detail', page=raffles.prev_num) \
        if raffles.has_prev else None
    return render_template('userdetail.html', user=user, raffles_count=raffles_count, participants_count=participants_count, devices_count=devices_count, feedbacks_count=feedbacks_count, logs_count=logs_count, raffles=raffles, next_url=next_url, prev_url=prev_url)


@app.route('/User/participants')
@login_required
def user_participants():
    id_share = request.args.get('id', 1)
    user = Users.query.filter_by(id_share=id_share).first()
    raffles_count = Raffles.query.filter_by(user_id=user.id).count()
    participants_count = Participants.query.filter_by(user_id=user.id).count()
    devices_count = Keys.query.filter_by(user_id=user.id).count()
    feedbacks_count = Feedbacks.query.filter_by(user_id=user.id).count()
    logs_count = Logs.query.filter_by(user_id=user.id).count()
    page = request.args.get('page', 1, type=int)
    raffles = db.session.query(Raffles.id,Raffles.id_share,Raffles.title,Participants.creation_date).join(Participants, Raffles.id == Participants.raffle_id).filter_by(user_id=user.id).order_by(desc(Participants.creation_date)).paginate(page, 15, False)
    next_url = url_for('user_participants', page=raffles.next_num) \
        if raffles.has_next else None
    prev_url = url_for('user_participants', page=raffles.prev_num) \
        if raffles.has_prev else None
    return render_template('userparticipants.html', user=user, raffles_count=raffles_count, participants_count=participants_count, devices_count=devices_count, feedbacks_count=feedbacks_count, logs_count=logs_count, raffles=raffles, next_url=next_url, prev_url=prev_url)


@app.route('/User/feedbacks')
@login_required
def user_feedbacks():
    id_share = request.args.get('id', 1)
    user = Users.query.filter_by(id_share=id_share).first()
    raffles_count = Raffles.query.filter_by(user_id=user.id).count()
    participants_count = Participants.query.filter_by(user_id=user.id).count()
    devices_count = Keys.query.filter_by(user_id=user.id).count()
    feedbacks_count = Feedbacks.query.filter_by(user_id=user.id).count()
    logs_count = Logs.query.filter_by(user_id=user.id).count()
    page = request.args.get('page', 1, type=int)
    feedbacks = db.session.query(Feedbacks).filter_by(user_id=user.id).order_by(desc(Feedbacks.id)).paginate(
        page, 15, False)
    next_url = url_for('user_feedbacks', page=feedbacks.next_num) \
        if feedbacks.has_next else None
    prev_url = url_for('user_feedbacks', page=feedbacks.prev_num) \
        if feedbacks.has_prev else None
    return render_template('userfeedbacks.html', user=user, raffles_count=raffles_count, participants_count=participants_count, devices_count=devices_count, feedbacks_count=feedbacks_count, logs_count=logs_count, feedbacks=feedbacks, next_url=next_url, prev_url=prev_url)


@app.route('/User/devices')
@login_required
def user_devices():
    id_share = request.args.get('id', 1)
    user = Users.query.filter_by(id_share=id_share).first()
    raffles_count = Raffles.query.filter_by(user_id=user.id).count()
    participants_count = Participants.query.filter_by(user_id=user.id).count()
    devices_count = Keys.query.filter_by(user_id=user.id).count()
    feedbacks_count = Feedbacks.query.filter_by(user_id=user.id).count()
    logs_count = Logs.query.filter_by(user_id=user.id).count()
    page = request.args.get('page', 1, type=int)
    devices = db.session.query(Keys.id,Deviceinformation.brand,Deviceinformation.model,Deviceinformation.release,Keys.creation_date,Keys.expiration).join(Keys, Deviceinformation.id == Keys.device_information_id).filter_by(user_id=user.id).order_by(desc(Keys.id)).paginate(page, 15, False)
    next_url = url_for('user_devices', page=devices.next_num) \
        if devices.has_next else None
    prev_url = url_for('user_devices', page=devices.prev_num) \
        if devices.has_prev else None
    return render_template('userdevices.html', user=user, raffles_count=raffles_count, participants_count=participants_count, devices_count=devices_count, feedbacks_count=feedbacks_count, logs_count=logs_count, devices=devices, next_url=next_url, prev_url=prev_url)


@app.route('/User/logs')
@login_required
def user_logs():
    id_share = request.args.get('id', 1)
    user = Users.query.filter_by(id_share=id_share).first()
    raffles_count = Raffles.query.filter_by(user_id=user.id).count()
    participants_count = Participants.query.filter_by(user_id=user.id).count()
    devices_count = Keys.query.filter_by(user_id=user.id).count()
    feedbacks_count = Feedbacks.query.filter_by(user_id=user.id).count()
    logs_count = Logs.query.filter_by(user_id=user.id).count()
    page = request.args.get('page', 1, type=int)
    logs = db.session.query(Logs).filter_by(user_id=user.id).order_by(desc(Logs.id)).paginate(
        page, 15, False)
    next_url = url_for('user_logs', page=logs.next_num) \
        if logs.has_next else None
    prev_url = url_for('user_logs', page=logs.prev_num) \
        if logs.has_prev else None
    return render_template('userlogs.html', user=user, raffles_count=raffles_count, participants_count=participants_count, devices_count=devices_count, feedbacks_count=feedbacks_count, logs_count=logs_count, logs=logs, next_url=next_url, prev_url=prev_url)


@app.route('/Raffles')
@login_required
def raffles_list():
    page = request.args.get('page', 1, type=int)
    raffles = db.session.query(Raffles).order_by(desc(Raffles.id)).paginate(page, 15, False)
    next_url = url_for('raffles_list', page=raffles.next_num) \
        if raffles.has_next else None
    prev_url = url_for('raffles_list', page=raffles.prev_num) \
        if raffles.has_prev else None
    return render_template('raffles.html', raffles=raffles, next_url=next_url, prev_url=prev_url)


@app.route('/Raffle/detail')
@login_required
def raffle_detail():
    id_share = request.args.get('id', 1)
    raffle = Raffles.query.filter_by(id_share=id_share).first()
    participants_count = Participants.query.filter_by(raffle_id=raffle.id).count()
    page = request.args.get('page', 1, type=int)
    participants = db.session.query(Participants.id,Users.id_share,Users.name,Users.profile_picture,Participants.creation_date).join(Participants, Users.id == Participants.user_id).filter_by(raffle_id=raffle.id).order_by(desc(Participants.id)).paginate(page, 15, False)
    next_url = url_for('raffle_detail', page=participants.next_num) \
        if participants.has_next else None
    prev_url = url_for('raffle_detail', page=participants.prev_num) \
        if participants.has_prev else None
    countries = db.session.query(Countries.country_code).join(Countrytargets,Countries.id == Countrytargets.country_id).filter_by(raffle_id=raffle.id).all()
    tags = db.session.query(Tags.tag_name).join(Tagtargets,Tags.id == Tagtargets.tag_id).filter_by(raffle_id=raffle.id).all()
    return render_template('raffledetail.html', raffle=raffle, participants_count=participants_count, participants=participants, countries=countries, tags=tags, next_url=next_url, prev_url=prev_url)


@app.route('/Raffle/lucky')
@login_required
def raffle_lucky():
    id_share = request.args.get('id', 1)
    raffle = Raffles.query.filter_by(id_share=id_share).first()
    participants_count = Participants.query.filter_by(raffle_id=raffle.id).count()
    lucky_winners = db.session.query(Users.id,Users.id_share,Users.name,Users.profile_picture,Luckys.creation_date,Luckys.check_key).join(Luckys, Users.id == Luckys.user_id).filter_by(status=True).filter_by(raffles_id=raffle.id).all()
    lucky_reserves = db.session.query(Users.id, Users.id_share, Users.name, Users.profile_picture, Luckys.creation_date,Luckys.check_key).join(Luckys, Users.id == Luckys.user_id).filter_by(status=False).filter_by(raffles_id=raffle.id).all()
    countries = db.session.query(Countries.country_code).join(Countrytargets,Countries.id == Countrytargets.country_id).filter_by(raffle_id=raffle.id).all()
    tags = db.session.query(Tags.tag_name).join(Tagtargets,Tags.id == Tagtargets.tag_id).filter_by(raffle_id=raffle.id).all()
    return render_template('rafflelucky.html', raffle=raffle, participants_count=participants_count, lucky_winners=lucky_winners, lucky_reserves=lucky_reserves, countries=countries, tags=tags)


@app.route('/Raffle/edit')
@login_required
def raffle_edit():
    id_share = request.args.get('id', 1)
    raffle = Raffles.query.filter_by(id_share=id_share).first()
    participants_count = Participants.query.filter_by(raffle_id=raffle.id).count()
    countries = db.session.query(Countries.country_code).join(Countrytargets,Countries.id == Countrytargets.country_id).filter_by(raffle_id=raffle.id).all()
    tags = db.session.query(Tags.tag_name).join(Tagtargets, Tags.id == Tagtargets.tag_id).filter_by(raffle_id=raffle.id).all()
    return render_template('raffleedit.html',raffle=raffle,countries=countries,tags=tags,participants_count=participants_count)


@app.route('/RaffleShow', methods=['POST'])
@login_required
def raffleshow():
        id_share = request.form['id']
        raffle = Raffles.query.filter_by(id_share=id_share).first()
        raffle_join_count = Participants.query.filter_by(raffle_id=raffle.id).count()
        tags = db.session.query(Tags.tag_name).join(Tagtargets,Tags.id == Tagtargets.tag_id).filter(Tagtargets.raffle_id == raffle.id).all()
        raffle_tag = []
        for tag in tags:
            item = {}
            item['text'] = str(tag[0])
            item['value'] = str(tag[0])
            raffle_tag.append(item)
        countries_selected = db.session.query(Countries.country_code).join(Countrytargets, Countries.id == Countrytargets.country_id).filter(
            Countrytargets.raffle_id == raffle.id).all()
        return jsonify(id=raffle.id_share,title=raffle.title,description=raffle.description,contact_information=raffle.contact_information,expiration=str(raffle.expiration),winners=raffle.winners,reserves=raffle.reserves,raffle_join_count=raffle_join_count,status=raffle.status,tags=raffle_tag,countries_selected=countries_selected,delete=raffle.delete,disable=raffle.disable)


@app.route('/RaffleCountriesList', methods=['POST'])
@login_required
def rafflecountrieslist():
    countries = db.session.query(Countries.country_code, Countrymultilang.country_name).join(Countrymultilang,Countries.country_code == Countrymultilang.country_code).filter_by(multi_code='en').order_by(Countrymultilang.country_name).all()
    data = []
    for country in countries:
        item = {}
        item["value"] = country.country_code
        item["text"] = country.country_name
        data.append(item)
    return jsonify(data)


@app.route('/RaffleUpdate', methods=['POST'])
@login_required
def raffleupdate():
    id_share = request.form['id']
    raffle = Raffles.query.filter_by(id_share=id_share).first()
    tags = request.form['tags']
    tags = tags.split(',')
    countries = request.form['countries']
    countries = countries.split(',')
    title = request.form['title']
    description = request.form['description']
    contact_information = request.form['contact_information']
    expiration = request.form['expiration']
    winners = request.form['winners']
    reserves = request.form['reserves']
    delete = request.form['delete']
    disable = request.form['disable']
    if title.strip() is "":
        return jsonify(result="the title cannot be blank",status=False)
    elif description.strip() is "":
        return jsonify(result="description cannot be left blank",status=False)
    elif contact_information.strip() is "":
        return jsonify(result="contact information cannot be blank",status=False)
    elif expiration.strip() is "":
        return jsonify(result="end date cannot be blank",status=False)
    elif winners.strip() is "":
        return jsonify(result="the number of winners cannot be blank", status=False)
    elif reserves.strip() is "":
        return jsonify(result="the number of replacement people cannot be blank", status=False)
    elif int(winners) <= 0:
        return jsonify(result="the number of people to win cannot be less than zero or zero",status=False)
    elif int(reserves) < 0:
        return jsonify(result="the number of backup contacts cannot be less than zero", status=False)
    elif int(len(title)) > 60:
        return jsonify(result="the title cannot be greater than 60 characters", status=False)
    elif int(len(description)) > 350:
        return jsonify(result="the description cannot be greater than 350 characters", status=False)
    elif int(len(contact_information)) > 350:
        return jsonify(result="contact information cannot be greater than 350 characters", status=False)
    elif int(winners) > 50:
        return jsonify(result="the number of people who will win can not be more than 50",status=False)
    elif int(reserves) > 50:
        return jsonify(result="the number of reserve persons cannot be more than 50", status=False)
    elif len(tags) < 2:
        return jsonify(result="at least two labels must be entered", status=False)
    elif len(tags) > 4:
        return jsonify(result="up to four labels must be entered", status=False)
    elif countries[0].strip() is "":
        return jsonify(result="At least one country must be selected", status=False)
    elif len(countries) > 10:
        return jsonify(result="A maximum of ten countries should be selected", status=False)
    else:
        raffle.title = title
        raffle.description = description
        raffle.contact_information = contact_information
        raffle.expiration = expiration
        raffle.winners = winners
        raffle.reserves = reserves
        raffle.delete = stringtobool(delete)
        raffle.disable = stringtobool(disable)
        raffle.last_update = datetime.utcnow()
        db.session.add(raffle)
        db.session.commit()
        add_tags(tags, raffle.id)
        add_countries(countries, raffle.id)
        return jsonify(result="raffle updated",status=True)


@app.route('/Feedbacks')
@login_required
def feedbacks_list():
    page = request.args.get('page', 1, type=int)
    feedbacks = db.session.query(Feedbacks.id,Feedbacks.creation_date,Feedbacks.last_update,Feedbacks.read,Users.name).join(Feedbacks,Users.id == Feedbacks.user_id).order_by(desc(Feedbacks.id)).paginate(page, 15, False)
    next_url = url_for('feedbacks_list', page=feedbacks.next_num) \
        if feedbacks.has_next else None
    prev_url = url_for('feedbacks_list', page=feedbacks.prev_num) \
        if feedbacks.has_prev else None
    return render_template('feedbacks.html', feedbacks=feedbacks, next_url=next_url, prev_url=prev_url)


@app.route('/FeedbackShow', methods=['POST'])
@login_required
def feedbackshow():
        id = request.form['id']
        feedback = db.session.query(Feedbacks.id, Feedbacks.description, Feedbacks.creation_date, Users.name, Users.id_share, Users.profile_picture).join(Feedbacks,Users.id == Feedbacks.user_id).filter_by(id=id).first()
        feedback_update = Feedbacks.query.filter_by(id=id).first()
        feedback_update.read = True
        feedback_update.last_update = datetime.utcnow()
        db.session.add(feedback_update)
        db.session.commit()
        return jsonify(description=feedback.description, creation_date=str(_jinja2_filter_datetime(feedback.creation_date)), name=feedback.name, user_id=feedback.id_share, profile_picture=feedback.profile_picture)


@app.route('/Versions')
@login_required
def versions_list():
    page = request.args.get('page', 1, type=int)
    versions = db.session.query(Versions).order_by(desc(Versions.id)).paginate(page, 15, False)
    next_url = url_for('versions_list', page=versions.next_num) \
        if versions.has_next else None
    prev_url = url_for('versions_list', page=versions.prev_num) \
        if versions.has_prev else None
    return render_template('versions.html', versions=versions, next_url=next_url, prev_url=prev_url)


@app.route('/VersionShow', methods=['POST'])
@login_required
def versionshow():
        id = request.form['id']
        version = db.session.query(Versions).filter_by(id=id).first()
        return jsonify(id=version.id,versions_name=version.versions_name,versions_code=version.versions_code,versions_description=version.versions_description,contact_secret_key=version.contact_secret_key,versions_secret_key=version.versions_secret_key,creation_date=str(_jinja2_filter_datetime(version.creation_date)),expiration=str(_jinja2_filter_datetime(version.expiration)))


@app.route('/VersionCreate', methods=['POST'])
@login_required
def versioncreate():
    version_name = request.form['version_name']
    version_code = request.form['version_code']
    description = request.form['description']
    expiration = request.form['expiration']
    if version_name.strip() is '':
        return jsonify(result="version name cannot be left blank",status=False)
    elif version_code.strip() is '':
        return jsonify(result="version code cannot be left blank", status=False)
    elif description.strip() is '':
        return jsonify(result="description cannot be left blank", status=False)
    elif expiration.strip() is '':
        return jsonify(result="expiration cannot be left blank", status=False)
    else:
        version = Versions()
        version.versions_name = version_name
        version.versions_code = version_code
        version.expiration = expiration
        version.versions_description = description
        version.contact_secret_key = aes_key_generator()
        version.versions_secret_key = md5(uuid.uuid4())
        version.creation_date = datetime.utcnow()
        db.session.add(version)
        db.session.commit()
        return jsonify(result="Version created", status=True)


@app.route('/VersionUpdatePost', methods=['POST'])
@login_required
def versionupdatepost():
    id = request.form['id']
    description = request.form['description']
    expiration = request.form['expiration']
    if description.strip() is '':
        return jsonify(result="description cannot be left blank", status=False)
    elif expiration.strip() is '':
        return jsonify(result="expiration cannot be left blank", status=False)
    else:
        version = Versions.query.filter_by(id=id).first()
        version.expiration = expiration
        version.versions_description = description
        db.session.add(version)
        db.session.commit()
        return jsonify(result="Version updated", status=True)


@app.route('/Login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/LoginPost', methods=['POST'])
def loginpost():
    username = request.form['username']
    password = request.form['password']
    rememberme = request.form['rememberme']
    if username.strip() is '':
        return jsonify(result="username cannot be left blank", status=False)
    elif password.strip() is '':
        return jsonify(result="password cannot be left blank", status=False)
    else:
        user = AdminUsers.query.filter_by(user_name=username).filter_by(password_hash=hashlib.md5(str(password).encode('utf-8')).hexdigest()).first()
        if user is not None:
            session['username'] = user.user_name
            session['password'] = user.password_hash
            rnd = random.randint(100000,999999)
            session['2fa'] = rnd
            send_mail(user.mail_address,'2FA',rnd)
            result = jsonify(result="2FA", status=True)
            if rememberme == 'true':
                result.set_cookie("remember_me", user.user_name)
            return result
        else:
            return jsonify(result="Username or password incorrect", status=False)


@app.route('/2FAPost', methods=['POST'])
def twofapost():
    code = request.form['code']
    if code.strip() is '':
        return jsonify(result="code cannot be left blank", status=False)
    else:
        twofa = str(session['2fa'])
        if code == twofa:
            username = session['username']
            password = session['password']
            user = AdminUsers.query.filter_by(user_name=username).filter_by(password_hash=password).first()
            login_user(user)
            return jsonify(result="Welcome", status=True)
        else:
            return jsonify(result="2Fa code incorrect", status=False)


@app.route('/Passwordchange', methods=['POST'])
def passwordchange():
    password = request.form['password']
    newpassword = request.form['newpassword']
    newpassword2 = request.form['newpassword2']
    if password.strip() is '':
        return jsonify(result="password cannot be left blank", status=False)
    elif newpassword.strip() is '':
        return jsonify(result="new password cannot be left blank", status=False)
    elif newpassword2.strip() is '':
        return jsonify(result="new password cannot be left blank", status=False)
    elif newpassword.strip() != newpassword2.strip():
        return jsonify(result="new password cannot be left blank", status=False)
    else:
        user = AdminUsers.query.filter_by(id=current_user.id).filter_by(password_hash=md5(password)).first()
        if user is not None:
            user = AdminUsers.query.filter_by(id=current_user.id).first()
            user.password_hash = md5(newpassword)
            user.last_update = datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            return jsonify(result="Password change", status=True)
        else:
            return jsonify(result="Fail", status=False)


@app.route('/Logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/Admin/Users')
@login_required
def admin_users_list():
    if current_user.master is True:
        page = request.args.get('page', 1, type=int)
        users = db.session.query(AdminUsers).order_by(desc(AdminUsers.id)).paginate(page, 15, False)
        next_url = url_for('admin_users_list', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('admin_users_list', page=users.prev_num) \
            if users.has_prev else None
        return render_template('adminusers.html', users=users, next_url=next_url, prev_url=prev_url)
    else:
        return jsonify(result="Access denied", status=False)


@app.route('/Admin/User/Show', methods=['POST'])
@login_required
def admin_user_show():
    if current_user.master is True:
        id = request.form['id']
        user = db.session.query(AdminUsers).filter_by(id=id).first()
        profile_picture = 'https://www.gravatar.com/avatar/'+md5(user.mail_address)+'?s=136'
        return jsonify(id=user.id,name=user.name,user_name=user.user_name,mail_address=user.mail_address,master=user.master,active=user.is_active,profile_picture=profile_picture,creation_date=str(_jinja2_filter_datetime(user.creation_date)),last_update=str(_jinja2_filter_datetime(user.last_update)))
    else:
        return jsonify(result="Access denied", status=False)


@app.route('/Admin/User/PasswordChange', methods=['POST'])
def admin_user_password_change():
    if current_user.master is True:
        user_id = request.form['id']
        newpassword = request.form['newpassword']
        newpassword2 = request.form['newpassword2']
        if newpassword.strip() is '':
            return jsonify(result="new password cannot be left blank", status=False)
        elif newpassword2.strip() is '':
            return jsonify(result="new password cannot be left blank", status=False)
        elif newpassword.strip() != newpassword2.strip():
            return jsonify(result="new password cannot be left blank 2", status=False)
        else:
            user = AdminUsers.query.filter_by(id=user_id).first()
            if user is not None:
                user = AdminUsers.query.filter_by(id=user_id).first()
                user.password_hash = md5(newpassword)
                user.last_update = datetime.utcnow()
                db.session.add(user)
                db.session.commit()
                return jsonify(result="Password change", status=True)
            else:
                return jsonify(result="Fail", status=False)
    else:
        return jsonify(result="Access denied", status=False)


@app.route('/Admin/User/Create', methods=['POST'])
@login_required
def admin_user_create():
    if current_user.master is True:
        name = request.form['name']
        username = request.form['username']
        mailaddress = request.form['mailaddress']
        password = request.form['password']
        master = request.form['master']
        if name.strip() is '':
            return jsonify(result="name cannot be left blank", status=False)
        elif username.strip() is '':
            return jsonify(result="user name cannot be left blank", status=False)
        elif mailaddress.strip() is '':
            return jsonify(result="mail address cannot be left blank", status=False)
        elif password.strip() is '':
            return jsonify(result="password cannot be left blank", status=False)
        elif master.strip() is '':
            return jsonify(result="master cannot be left blank", status=False)
        else:
            adminuser = AdminUsers()
            adminuser.name = name
            adminuser.user_name = username
            adminuser.mail_address = mailaddress
            adminuser.password_hash = md5(password)
            adminuser.master = bool(str(master).capitalize())
            adminuser.is_active = True
            adminuser.creation_date = datetime.utcnow()
            adminuser.last_update = datetime.utcnow()
            db.session.add(adminuser)
            db.session.commit()
            return jsonify(result="User created", status=True)
    else:
        return jsonify(result="Access denied", status=False)


@app.route('/Admin/User/Update', methods=['POST'])
@login_required
def admin_user_update():
    if current_user.master is True:
        user_id = request.form['id']
        name = request.form['name']
        username = request.form['username']
        mailaddress = request.form['mailaddress']
        master = request.form['master']
        active = request.form['active']
        if name.strip() is '':
            return jsonify(result="name cannot be left blank", status=False)
        elif username.strip() is '':
            return jsonify(result="user name cannot be left blank", status=False)
        elif mailaddress.strip() is '':
            return jsonify(result="mail address cannot be left blank", status=False)
        elif master.strip() is '':
            return jsonify(result="master cannot be left blank", status=False)
        elif active.strip() is '':
            return jsonify(result="active cannot be left blank", status=False)
        else:
            adminuser = AdminUsers.query.filter_by(id=user_id).first()
            adminuser.name = name
            adminuser.user_name = username
            adminuser.mail_address = mailaddress
            adminuser.master = stringtobool(master)
            adminuser.is_active = stringtobool(active)
            adminuser.last_update = datetime.utcnow()
            db.session.add(adminuser)
            db.session.commit()
            return jsonify(result="User updated", status=True)
    else:
        return jsonify(result="Access denied", status=False)


@app.route('/Socialmedia')
@login_required
def socialmedia_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', None)
    if search is not None:
        socialmedias = db.session.query(Socialmedia).filter_by(author_name=search).order_by(desc(Socialmedia.id)).paginate(page, 999, False)
    else:
        socialmedias = db.session.query(Socialmedia).order_by(desc(Socialmedia.id)).paginate(page, 15, False)
    next_url = url_for('socialmedia_list', page=socialmedias.next_num) \
        if socialmedias.has_next else None
    prev_url = url_for('socialmedia_list', page=socialmedias.prev_num) \
        if socialmedias.has_prev else None
    return render_template('socialmedia.html', socialmedias=socialmedias, next_url=next_url, prev_url=prev_url)


@app.route('/Socialmedia/verified')
@login_required
def socialmedia_verified_list():
    page = request.args.get('page', 1, type=int)
    socialmedias = db.session.query(Socialmedia).filter_by(verification=True).order_by(desc(Socialmedia.id)).paginate(page, 15, False)
    next_url = url_for('socialmedia_verified_list', page=socialmedias.next_num) \
        if socialmedias.has_next else None
    prev_url = url_for('socialmedia_verified_list', page=socialmedias.prev_num) \
        if socialmedias.has_prev else None
    return render_template('socialmediaverified.html', socialmedias=socialmedias, next_url=next_url, prev_url=prev_url)


@app.route('/Socialmedia/verification')
@login_required
def socialmedia_verification_list():
    page = request.args.get('page', 1, type=int)
    socialmedias = db.session.query(Socialmedia).filter_by(verification=False).order_by(Socialmedia.id).paginate(page, 15, False)
    next_url = url_for('socialmedia_verification_list', page=socialmedias.next_num) \
        if socialmedias.has_next else None
    prev_url = url_for('socialmedia_verification_list', page=socialmedias.prev_num) \
        if socialmedias.has_prev else None
    return render_template('socialmediaverification.html', socialmedias=socialmedias, next_url=next_url, prev_url=prev_url)


@app.route('/Socialmedia/disable')
@login_required
def socialmedia_disable_list():
    page = request.args.get('page', 1, type=int)
    socialmedias = db.session.query(Socialmedia).filter_by(disable=True).order_by(desc(Socialmedia.id)).paginate(page, 15, False)
    next_url = url_for('socialmedia_disable_list', page=socialmedias.next_num) \
        if socialmedias.has_next else None
    prev_url = url_for('socialmedia_disable_list', page=socialmedias.prev_num) \
        if socialmedias.has_prev else None
    return render_template('socialmediadisable.html', socialmedias=socialmedias, next_url=next_url, prev_url=prev_url)


@app.route('/Socialmedia/delete')
@login_required
def socialmedia_delete_list():
    page = request.args.get('page', 1, type=int)
    socialmedias = db.session.query(Socialmedia).filter_by(delete=True).order_by(desc(Socialmedia.id)).paginate(page, 15, False)
    next_url = url_for('socialmedia_delete_list', page=socialmedias.next_num) \
        if socialmedias.has_next else None
    prev_url = url_for('socialmedia_delete_list', page=socialmedias.prev_num) \
        if socialmedias.has_prev else None
    return render_template('socialmediadelete.html', socialmedias=socialmedias, next_url=next_url, prev_url=prev_url)


@app.route('/Socialmedia/sponsor')
@login_required
def socialmedia_sponsor_list():
    page = request.args.get('page', 1, type=int)
    socialmedias = db.session.query(Socialmedia).filter_by(sponsor=True).order_by(desc(Socialmedia.id)).paginate(page, 15, False)
    next_url = url_for('socialmedia_sponsor_list', page=socialmedias.next_num) \
        if socialmedias.has_next else None
    prev_url = url_for('socialmedia_sponsor_list', page=socialmedias.prev_num) \
        if socialmedias.has_prev else None
    return render_template('socialmediasponsor.html', socialmedias=socialmedias, next_url=next_url, prev_url=prev_url)


@app.route('/Socialmedia/detail')
@login_required
def socialmedia_detail():
    id_share = request.args.get('id', 1)
    socialmedia = Socialmedia.query.filter_by(id_share=id_share).first()
    socialstatistics_count = Socialstatistics.query.filter_by(social_id=socialmedia.id, clicks=False).count()
    socialstatistics_clicks_count = Socialstatistics.query.filter_by(social_id=socialmedia.id, clicks=True).count()
    saved_count = Socialsaved.query.filter_by(social_id=socialmedia.id).count()
    page = request.args.get('page', 1, type=int)
    socialstatistics = db.session.query(Socialstatistics.id,Users.id_share,Users.name,Users.profile_picture,Socialstatistics.creation_date,Socialstatistics.clicks).join(Socialstatistics, Users.id == Socialstatistics.user_id).filter_by(social_id=socialmedia.id).order_by(desc(Socialstatistics.id)).paginate(page, 20, False)
    author_image = instagram_profile_image(socialmedia.author_name)
    next_url = url_for('socialmedia_detail', page=socialstatistics.next_num) \
        if socialstatistics.has_next else None
    prev_url = url_for('socialmedia_detail', page=socialstatistics.prev_num) \
        if socialstatistics.has_prev else None
    countries = db.session.query(Countries.country_code).join(Socialcountrytargets,Countries.id == Socialcountrytargets.country_id).filter_by(social_id=socialmedia.id).all()
    tags = db.session.query(Tags.tag_name).join(Socialtagtargets,Tags.id == Socialtagtargets.tag_id).filter_by(social_id=socialmedia.id).all()
    return render_template('socialmediadetail.html', socialmedia=socialmedia, socialstatistics_count=socialstatistics_count, socialstatistics_clicks_count=socialstatistics_clicks_count, socialstatistics=socialstatistics, countries=countries, tags=tags, next_url=next_url, prev_url=prev_url, author_image=author_image, saved_count=saved_count)


@app.route('/Socialmedia/saved')
@login_required
def socialmedia_saved():
    id_share = request.args.get('id', 1)
    socialmedia = Socialmedia.query.filter_by(id_share=id_share).first()
    socialstatistics_count = Socialstatistics.query.filter_by(social_id=socialmedia.id, clicks=False).count()
    socialstatistics_clicks_count = Socialstatistics.query.filter_by(social_id=socialmedia.id, clicks=True).count()
    saved_count = Socialsaved.query.filter_by(social_id=socialmedia.id).count()
    page = request.args.get('page', 1, type=int)
    socialsaveds = db.session.query(Socialsaved.id,Users.id_share,Users.name,Users.profile_picture,Socialsaved.creation_date).join(Socialsaved, Users.id == Socialsaved.user_id).filter_by(social_id=socialmedia.id).order_by(desc(Socialsaved.id)).paginate(page, 20, False)
    author_image = instagram_profile_image(socialmedia.author_name)
    next_url = url_for('socialmedia_saved', page=socialsaveds.next_num) \
        if socialsaveds.has_next else None
    prev_url = url_for('socialmedia_saved', page=socialsaveds.prev_num) \
        if socialsaveds.has_prev else None
    countries = db.session.query(Countries.country_code).join(Socialcountrytargets,Countries.id == Socialcountrytargets.country_id).filter_by(social_id=socialmedia.id).all()
    tags = db.session.query(Tags.tag_name).join(Socialtagtargets,Tags.id == Socialtagtargets.tag_id).filter_by(social_id=socialmedia.id).all()
    return render_template('socialmediasaved.html', socialmedia=socialmedia, socialstatistics_count=socialstatistics_count, socialstatistics_clicks_count=socialstatistics_clicks_count, socialsaveds=socialsaveds, countries=countries, tags=tags, next_url=next_url, prev_url=prev_url, author_image=author_image, saved_count=saved_count)


@app.route('/Socialmedia/edit')
@login_required
def socialmedia_edit():
    id_share = request.args.get('id', 1)
    socialmedia = Socialmedia.query.filter_by(id_share=id_share).first()
    socialstatistics_count = Socialstatistics.query.filter_by(social_id=socialmedia.id, clicks=False).count()
    socialstatistics_clicks_count = Socialstatistics.query.filter_by(social_id=socialmedia.id, clicks=True).count()
    saved_count = Socialsaved.query.filter_by(social_id=socialmedia.id).count()
    author_image = instagram_profile_image(socialmedia.author_name)
    countries = db.session.query(Countries.country_code).join(Socialcountrytargets,Countries.id == Socialcountrytargets.country_id).filter_by(social_id=socialmedia.id).all()
    tags = db.session.query(Tags.tag_name).join(Socialtagtargets,Tags.id == Socialtagtargets.tag_id).filter_by(social_id=socialmedia.id).all()
    return render_template('socialmediaedit.html', socialmedia=socialmedia, socialstatistics_count=socialstatistics_count, socialstatistics_clicks_count=socialstatistics_clicks_count, countries=countries, tags=tags, author_image=author_image, saved_count=saved_count)


@app.route('/SocialmediaTagsList', methods=['POST'])
@login_required
def socialmediataglist():
        id_share = request.form['id']
        socialmedia = Socialmedia.query.filter_by(id_share=id_share).first()
        tags = db.session.query(Tags.tag_name).join(Socialtagtargets,Tags.id == Socialtagtargets.tag_id).filter(Socialtagtargets.social_id == socialmedia.id).all()
        raffle_tag = []
        for tag in tags:
            item = {}
            item['text'] = str(tag[0])
            item['value'] = str(tag[0])
            raffle_tag.append(item)
        countries_selected = db.session.query(Countries.country_code).join(Socialcountrytargets, Countries.id == Socialcountrytargets.country_id).filter(
            Socialcountrytargets.social_id == socialmedia.id).all()
        return jsonify(tags=raffle_tag,countries_selected=countries_selected)


@app.route('/SocialmediaCountriesList', methods=['POST'])
@login_required
def socialmediacountrieslist():
    countries = db.session.query(Countries.country_code, Countrymultilang.country_name).join(Countrymultilang,Countries.country_code == Countrymultilang.country_code).filter_by(multi_code='en').order_by(Countrymultilang.country_name).all()
    data = []
    for country in countries:
        item = {}
        item["value"] = country.country_code
        item["text"] = country.country_name
        data.append(item)
    return jsonify(data)


@app.route('/SocialmediaUpdate', methods=['POST'])
@login_required
def SocialmediaUpdate():
    id_share = request.form['id']
    socialmedia = Socialmedia.query.filter_by(id_share=id_share).first()
    tags = request.form['tags']
    tags = tags.split(',')
    countries = request.form['countries']
    countries = countries.split(',')
    description = request.form['description']
    sponsor = request.form['sponsor']
    verification = request.form['verification']
    type = request.form['type']
    delete = request.form['delete']
    disable = request.form['disable']

    if description.strip() is "":
        return jsonify(result="description cannot be left blank",status=False)
    elif len(tags) < 2:
        return jsonify(result="at least two labels must be entered", status=False)
    elif len(tags) > 4:
        return jsonify(result="up to four labels must be entered", status=False)
    elif countries[0].strip() is "":
        return jsonify(result="At least one country must be selected", status=False)
    elif len(countries) > 10:
        return jsonify(result="A maximum of ten countries should be selected", status=False)
    else:
        socialmedia.media_description = description
        socialmedia.sponsor = stringtobool(sponsor)
        socialmedia.verification = stringtobool(verification)
        socialmedia.type = stringtobool(type)
        socialmedia.delete = stringtobool(delete)
        socialmedia.disable = stringtobool(disable)
        socialmedia.last_update = datetime.utcnow()
        db.session.add(socialmedia)
        db.session.commit()
        add_social_tags(tags, socialmedia.id)
        add_social_countries(countries, socialmedia.id)
        return jsonify(result="raffle updated",status=True)


@app.route('/socialmedia/statistics/count', methods=['POST'])
@login_required
def socialmedia_statistics():
    no_filter_statistics = Socialmedia.query.count()
    verified_statistics = Socialmedia.query.filter_by(verification=True).count()
    verification_statistics = Socialmedia.query.filter_by(verification=False).count()
    disable_statistics = Socialmedia.query.filter_by(disable=True).count()
    delete_statistics = Socialmedia.query.filter_by(delete=True).count()
    sponsor_statistics = Socialmedia.query.filter_by(sponsor=True).count()
    return jsonify(no_filter_statistics=no_filter_statistics,verified_statistics=verified_statistics,verification_statistics=verification_statistics,disable_statistics=disable_statistics,delete_statistics=delete_statistics,sponsor_statistics=sponsor_statistics)


@app.route('/Socialmedia/Show', methods=['POST'])
@login_required
def socialmedia_show():
        id = request.form['id']
        socialmedia = db.session.query(Socialmedia).filter_by(id_share=id).first()
        tags = db.session.query(Tags.tag_name).join(Socialtagtargets, Tags.id == Socialtagtargets.tag_id).filter(
            Socialtagtargets.social_id == socialmedia.id).all()
        countries_selected = db.session.query(Countries.country_code).join(Socialcountrytargets,
                                                                           Countries.id == Socialcountrytargets.country_id).filter(
            Socialcountrytargets.social_id == socialmedia.id).all()
        raffle_tag = []
        for tag in tags:
            item = {}
            item['text'] = str(tag[0])
            item['value'] = str(tag[0])
            raffle_tag.append(item)
        author_image = instagram_profile_image(socialmedia.author_name)
        return jsonify(id_share=socialmedia.id_share,author_name=socialmedia.author_name,author_image=author_image,media_image=socialmedia.media_image,description=socialmedia.media_description, creation_date=str(_jinja2_filter_datetime(socialmedia.creation_date)),tags=raffle_tag,countries=countries_selected)


@app.route('/Socialmedia/warnings')
@login_required
def warnings_list():
    page = request.args.get('page', 1, type=int)
    warnings = db.session.query(Socialreports.id,Socialreports.creation_date,Socialreports.read,Users.name,Socialreports.social_id).join(Socialreports,Users.id == Socialreports.user_id).order_by(desc(Socialreports.id)).paginate(page, 15, False)
    next_url = url_for('warnings_list', page=warnings.next_num) \
        if warnings.has_next else None
    prev_url = url_for('warnings_list', page=warnings.prev_num) \
        if warnings.has_prev else None
    return render_template('socialmediawarnings.html', warnings=warnings, next_url=next_url, prev_url=prev_url)


@app.route('/WarningsShow', methods=['POST'])
@login_required
def warningsshow():
        id = request.form['id']
        warning = db.session.query(Socialreports.id, Socialreports.description, Socialreports.creation_date, Users.name, Users.id_share, Users.profile_picture).join(Socialreports,Users.id == Socialreports.user_id).filter_by(id=id).first()
        socialreport_update = Socialreports.query.filter_by(id=id).first()
        socialreport_update.read = True
        socialreport_update.last_update = datetime.utcnow()
        db.session.add(socialreport_update)
        db.session.commit()
        return jsonify(description=warning.description, creation_date=str(_jinja2_filter_datetime(warning.creation_date)), name=warning.name, user_id=warning.id_share, profile_picture=warning.profile_picture)


@app.route('/Warnings/socialmedia/Show', methods=['POST'])
@login_required
def warnings_socialmedia_show():
    id = request.form['id']
    socialmedia = db.session.query(Socialmedia).filter_by(id=id).first()
    tags = db.session.query(Tags.tag_name).join(Socialtagtargets, Tags.id == Socialtagtargets.tag_id).filter(
        Socialtagtargets.social_id == socialmedia.id).all()
    countries_selected = db.session.query(Countries.country_code).join(Socialcountrytargets,
                                                                       Countries.id == Socialcountrytargets.country_id).filter(
        Socialcountrytargets.social_id == socialmedia.id).all()
    raffle_tag = []
    for tag in tags:
        item = {}
        item['text'] = str(tag[0])
        item['value'] = str(tag[0])
        raffle_tag.append(item)
    author_image = instagram_profile_image(socialmedia.author_name)
    return jsonify(id_share=socialmedia.id_share, author_name=socialmedia.author_name, author_image=author_image,
                   media_image=socialmedia.media_image, description=socialmedia.media_description,
                   creation_date=str(_jinja2_filter_datetime(socialmedia.creation_date)), tags=raffle_tag,
                   countries=countries_selected)


@app.route('/Socialmedia/add')
@login_required
def socialmedia_add():
    return render_template('socialmediaadd.html')


@app.route('/Socialmedia/create', methods=['POST'])
def socialmedia_create():
    media_url = request.form['link']
    tags = request.form['tags']
    countries = request.form['countries']
    verification = request.form['verification']
    type = request.form['type']

    tags = tags.replace('[', '')
    tags = tags.replace(']', '')
    countries = countries.replace('[', '')
    countries = countries.replace(']', '')
    tags = tags.split(',')
    countries = countries.split(',')

    while ('' in tags):
        tags.remove('')

    while ('' in countries):
        countries.remove('')

    if len(tags) < 2:
        return jsonify(api_result="at least two labels must be entered", status=False)
    elif len(tags) > 4:
        return jsonify(api_result="up to four labels must be entered", api_status=False)
    elif len(countries) == 0:
        return jsonify(api_result="At least one country must be selected", api_status=False)
    elif len(countries) > 10:
        return jsonify(api_result="A maximum of ten countries should be selected", api_status=False)
    elif media_url == '':
        return jsonify(api_result="url cannot be empty", api_status=False)
    else:
        parse = urlparse(media_url)
        media_url = "https://"+parse.netloc+parse.path
        if parse.netloc == "www.instagram.com" or parse.netloc == "instagram.com":
            try:
                with urllib.request.urlopen("https://api.instagram.com/oembed/?url=" + media_url) as url:
                    data = json.loads(url.read().decode())
                    media_shortcode = parse.path.replace('p', '', 1)
                    media_shortcode = media_shortcode.replace('/', '')
                    socialmedia = Socialmedia.query.filter_by(media_id=data["media_id"]).first()
                    if socialmedia is not None:
                        return jsonify(api_status=False, api_result="raffle added")
                    else:
                        socialmedia = Socialmedia()
                        socialmedia.id_share = uuid_short()
                        socialmedia.author_name = data["author_name"]
                        socialmedia.media_id = media_shortcode
                        socialmedia.media_description = data["title"]
                        socialmedia.media_image = 'https://instagram.com/p/'+media_shortcode+'/media/?size=l'
                        socialmedia.media_url = media_url
                        socialmedia.provider_name = data["provider_name"]
                        socialmedia.delete = False
                        socialmedia.disable = False
                        socialmedia.verification = stringtobool(verification)
                        socialmedia.sponsor = False
                        socialmedia.type = stringtobool(type)
                        socialmedia.creation_date = datetime.utcnow()
                        socialmedia.last_update = datetime.utcnow()
                        db.session.add(socialmedia)
                        db.session.commit()
                        add_social_tags(tags, socialmedia.id)
                        add_social_countries(countries, socialmedia.id)
                        return jsonify(api_status=True, api_result="raffle created")
            except ValueError:
                return jsonify(api_status=False, api_result="404 not found")
        else:
            return jsonify(api_status=False, api_result="invalid url")


@app.route('/Socialmedia/verified', methods=['POST'])
@login_required
def socialmedia_verified_update():
        id_share = request.form['id']
        socialmedia = Socialmedia.query.filter_by(id_share=id_share).first()
        if socialmedia.verification:
            socialmedia.verification = False
            socialmedia.last_update = datetime.utcnow()
            db.session.add(socialmedia)
            db.session.commit()
            return jsonify(api_status=False, api_result="Unverified")
        else:
            socialmedia.verification = True
            socialmedia.last_update = datetime.utcnow()
            db.session.add(socialmedia)
            db.session.commit()
            return jsonify(api_status=True, api_result="Verified")


@app.route('/Bgimage')
def bgimage():
    with urllib.request.urlopen("https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US") as url:
        data = json.loads(url.read().decode())
    data = "https://www.bing.com"+data["images"][0]["url"]
    return redirect(data, code=302)


if __name__ == '__main__':
    app.run(host='192.168.1.3',debug=True)
