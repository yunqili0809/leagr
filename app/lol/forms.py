from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField, TelField
from wtforms import validators, StringField, PasswordField, TextAreaField, SubmitField,BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_ckeditor import CKEditorField


from .. import db

