from flask import Blueprint

lol = Blueprint('lol', __name__)

from . import views, forms
