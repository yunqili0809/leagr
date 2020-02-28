from flask import Blueprint

main = Blueprint('lol', __name__)

from . import views, forms
