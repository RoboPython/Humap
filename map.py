from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash
from contextlib import closing
import yrs_apis

CONFIG_LOCATION='settings'
DATABASE = '/home/mancub/Dev/DB/maps.db'
DEBUG = True
SECRET_KEY = 'Xc93lKE0dQ'
USERNAME = 'admin'
PASSWORD = 'yrs2012'


app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        request.form['to_address']
        request.form['from_address']
        directions_response = yrs_apis.get_directions(request.form['from_address'], request.form['to_address'])
        user_input = {'to_address': request.form['to_address'], 'from_address': request.form['from_address'],'directions_data':directions_response}
        return render_template('results.html', user_input = user_input)
    else:
        return render_template('search.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)