from flask import (
    Blueprint, redirect, url_for, render_template, request, flash   
)

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    return "FasterVibes API"