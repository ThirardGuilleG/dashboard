from flask import Blueprint, flash, url_for, request, abort
from flask.templating import render_template
from werkzeug.utils import redirect
from database.models import User, UserType, get_db
from werkzeug.security import generate_password_hash, check_password_hash
from Blueprint.auth.models import SignUpForm, SignInForm
from loguru import logger
from urllib.parse import urlparse, urljoin
from flask_login import login_required, logout_user, login_user
from sqlalchemy import or_
import sqlite3

authB = Blueprint('auth', __name__)

db = get_db()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@authB.route('/login', methods=['GET','POST'])
def login():
    form = SignInForm()
    if form.validate_on_submit():
        user_or_email = form.user_or_email.data
        
        user = User.query.filter(or_(User.username==user_or_email, User.email==user_or_email)).first()
        # si user existe pas ou mot de passe faux
        if not user or not user.check_password(form.password.data):
            flash('Veuillez vérifier votre user ou mot de passe', 'error')
            return redirect(url_for('auth.login'))
        # Connection
        login_user(user)
        flash('connection réussie', "success")
        # Redirection vers url précédent
        next = request.args.get('next')
        if not is_safe_url(next) and next is not None:
            return abort(400)
        return redirect(url_for('index'))
    return render_template('form.html', form=form)


@authB.route('/signup', methods=['GET','POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        
        # par défaut regular
        type = UserType.regular.value
        newUser = User(type=type)
        form.populate_obj(newUser)
        newUser.set_password(form.password.data)
        try:
            db.session.add(newUser)
            db.session.commit()
        except sqlite3.Error as errBDD:
            logger.exception(f"erreur : {errBDD}")
            flash("Erreur dans la connection", "error")
        flash("Inscription réussie", "success")
        return redirect(url_for('auth.login'))
    return render_template('form.html', form=form)



@authB.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('Deconnection réussi.', "success")
    return redirect(url_for('index'))