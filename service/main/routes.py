from flask import Blueprint, url_for, redirect, render_template, request
from flask_cors import cross_origin


main = Blueprint('main', __name__)


@cross_origin()
@main.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main/home.html',
                           host=request.host_url + 'en/api',
                           title='Home')
