from flask import Blueprint

passthrough_bp = Blueprint('passthrough', __name__)

from . import views
