import pyfirmata
from flask import render_template, flash, redirect, url_for
from flask import request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.models import User, Casa, Led, Sensor, EstadoLed, EstadoSensor
from app.forms import LedControl
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import RegCasa, RegLed, RegSensor
from app import board

@app.route('/')
@app.route('/index')
@login_required
def index():
    if not current_user.is_authenticated:
        return render_template('index.html', title='Home')
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    casas = Casa.query.filter_by(propietario=user)

    return render_template('index.html', title='Home', casas=casas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Ingresar', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/ledcontrol/<lid>', methods=['GET', 'POST'])
@login_required
def ledcontrol(lid):
    led = Led.query.get(lid)
    form = LedControl()

    if form.validate_on_submit():
        if int(form.estado_pin.data) == 1:
            board.digital[led.puerto].write(1)
            sl = EstadoLed(status='encendido', led=led)
            db.session.add(sl)
            db.session.commit()
        else:
            board.digital[led.puerto].write(0)
            sl = EstadoLed(status='apagado', led=led)
            db.session.add(sl)
            db.session.commit()
        pass

    return render_template('ledcontrol.html', title='Led Control', form=form, led=led)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Felicidades, tu estas registrado ahora!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registro', form=form)


@app.route('/regcasa', methods=['GET', 'POST'])
@login_required
def regcasa():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    user_id = current_user.get_id()
    form = RegCasa()
    user = User.query.get(user_id)
    if form.validate_on_submit():
        home = Casa(address=form.address.data, propietario=user)
        db.session.add(home)
        db.session.commit()
        flash('Felicidades, has registrado tu casa!')
        return redirect(url_for('index'))
    return render_template('regcasa.html', title='Registro casa', user=user, form=form)


@app.route('/regled/<cid>', methods=['GET', 'POST'])
@login_required
def regled(cid):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegLed()
    home = Casa.query.get(cid)
    if form.validate_on_submit():
        farol = Led(puerto=form.puerto.data, domicilio=home)
        db.session.add(farol)
        db.session.commit()
        flash('Felicidades, has registrado un farol!')
        return redirect(url_for('casa', cid=cid))
    return render_template('regled.html', title='Registro farol', home=home, form=form)


@app.route('/regsensor/<cid>', methods=['GET', 'POST'])
@login_required
def regsensor(cid):
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegSensor()
    home = Casa.query.get(cid)
    if form.validate_on_submit():
        sen = Sensor(puerto=form.puerto.data, domicilio=home)
        db.session.add(sen)
        db.session.commit()
        flash('Felicidades, has registrado un sensor!')
        return redirect(url_for('index'))
    return render_template('regsensor.html', title='Registro sensor', home=home, form=form)


@app.route('/casa')
@login_required
def casa():
    casa_id = request.args.get('cid')
    home = Casa.query.get(casa_id)
    leds = Led.query.filter(Led.domicilio.has(id=casa_id)).all()
    sensores = Sensor.query.filter(Sensor.domicilio.has(id=casa_id)).all()
    return render_template('casa.html', casa=home, leds=leds, sensores=sensores)
