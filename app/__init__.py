import datetime
from datetime import datetime
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import current_user, login_required, RoleMixin, Security, \
    SQLAlchemyUserDatastore, UserMixin, utils
from flask_uploads import configure_uploads
from flaskext.markdown import Markdown

from .extensions import db, uploaded_images, security, mail, migrate, admin, ckeditor, moment
from .models import User, Role, Post, Tag
from .models.main import UserAdmin, RoleAdmin, PostAdmin # not db tables
from .main.forms import ExtendedRegisterForm

def crash_page(e):
    return render_template('main/500.html'), 500

def page_not_found(e):
    return render_template('main/404.html'), 404

def page_forbidden(e):
    return render_template('main/403.html'), 403


# sort of like an application factory
def create_app(config_name):
    app = Flask(__name__) # most of the work done right here
    app.config.from_object('settings') # load my settings / privat.py stuff
    
    # load my images uploader extension
    configure_uploads(app, uploaded_images)
    
    db.init_app(app) # load my database extension
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # load my security extension
    security.init_app(app, user_datastore, confirm_register_form=ExtendedRegisterForm)
    mail.init_app(app) # load my mail extension
    # load my writing tool extension
    md = Markdown(app, extensions=['fenced_code', 'tables'])
    migrate.init_app(app, db) # load my database upgrader tool
    moment.init_app(app)
    # TODO: don't be lazy, Mr.A, get rid of this try-expect
    # Add Flask-Admin views for Users and Roles
    try:
        admin.init_app(app)
        ckeditor.init_app(app)
        admin.add_view(UserAdmin(User, db.session))
        admin.add_view(RoleAdmin(Role, db.session))
        admin.add_view(PostAdmin(Post, db.session))
    except Exception as e:
        pass
        # TODO: log error

    # sentry_sdk.init(dsn="", integrations=[FlaskIntegration()])
    # Activate the flaskinni blueprint(my bundle of routes)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    from .lol import lol as lol_blueprint
    app.register_blueprint(lol_blueprint)

    # custom error handlers, these called functions at the top of the file
    app.register_error_handler(500, crash_page)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, page_forbidden)


    # Executes before the first request is processed.
    @app.before_first_request
    def before_first_request():

        # Create any database tables that don't exist yet.
        db.create_all()

        # Create the Roles "admin" and "end-user" -- unless they already exist
        user_datastore.find_or_create_role(name='admin', description='Administrator')
        user_datastore.find_or_create_role(name='end-user', description='End user')

        # Create two Users for testing purposes -- unless they already exists.
        # In each case, use Flask-Security utility function to encrypt the password.
        encrypted_password = utils.encrypt_password(app.config['STARTING_ADMIN_PASS'])
        for email in app.config['STARTING_ADMINS']:
            if not user_datastore.get_user(email):
                user_datastore.create_user(email=email, password=encrypted_password)
            

        # Commit any database changes; the User and Roles must exist before we can add a Role to the User
        db.session.commit()

        # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
        # Users already have these Roles.) Again, commit any database changes.
        for email in app.config['STARTING_ADMINS']:
            user_datastore.add_role_to_user(email, 'admin')
            confirmed_admin = user_datastore.get_user(email)
            confirmed_admin.confirmed_at = datetime.utcnow()

        db.session.commit()

    
    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            first_time = True if not current_user.last_seen else False
            current_user.last_seen = datetime.utcnow()
            db.session.commit()


    return app


