#!/usr/bin/env python

import sqlite3
import base64
import json

import flask
from flask_bootstrap import Bootstrap

from data_filter_example import opa

app = flask.Flask(__name__, static_url_path='/static')
Bootstrap(app)

def get_pet(pet_id):
    decision = query_opa("GET", ["pets", pet_id])
    if not decision.defined:
        raise flask.abort(403)

    sql = opa.splice(SELECT='pets.*', FROM='pets', WHERE='pets.id=?', decision=decision)

    result = query_db(sql, args=(pet_id,), one=True)
    if result is None:
        raise flask.abort(404)

    return result


def list_pets():
    decision = query_opa("GET", ["pets"])
    if not decision.defined:
        raise flask.abort(403)

    sql = opa.splice(SELECT='pets.*', FROM='pets', decision=decision)

    return query_db(sql)


def create_pet(pet):
    decision = query_opa("POST", ["pets"], pet=pet)
    if not decision.defined:
        raise flask.abort(403)

    elif decision.sql is not None:
        # POST API does not support conditional results.
        raise flask.abort(500)

    db = get_db()
    c = db.cursor()
    insert_pet(c, pet)
    db.commit()


def query_opa(method, path, **kwargs):
    input = {
        'method': method,
        'path': path,
        'subject': make_subject(),
    }
    for key in kwargs:
        input[key] = kwargs[key]
    return opa.compile(q='data.example.allow = true',
                       input=input,
                       unknowns=['pets'])


@app.route('/api/pets/<pet_id>', methods=["GET"])
def api_get_pet(pet_id):
    return flask.jsonify(get_pet(pet_id))


@app.route('/api/pets', methods=["GET"])
def api_list_pets():
    return flask.jsonify(list_pets())


@app.route('/api/pets', methods=["POST"])
def api_create_pet():
    pet = flask.request.get_json(force=True)
    return flask.jsonify(create_pet(pet))


@app.route('/')
def index():
    kwargs = {
        'username': flask.request.cookies.get('user', ''),
        'pets': list_pets(),
    }
    if kwargs['username'] in USERS:
        kwargs['user'] = USERS[kwargs['username']]
    return flask.render_template('index.html', **kwargs)


@app.route('/login', methods=['POST'])
def login():
    user = flask.request.values.get('username')
    response = app.make_response(flask.redirect(flask.request.referrer))
    response.set_cookie('user', user)
    if user in USERS:
        for c in COOKIES:
            if c in USERS[user]:
                response.set_cookie(c, base64.b64encode(json.dumps(USERS[user][c])))
    return response


@app.route('/logout', methods=['GET'])
def logout():
    response = app.make_response(flask.redirect(flask.request.referrer))
    response.set_cookie('user', '', expires=0)
    for c in COOKIES:
        response.set_cookie(c, '', expires=0)
    return response


def make_subject():
    subject = {}
    subject['user'] = flask.request.cookies.get('user', 'anonymous')
    for c in COOKIES:
        v = flask.request.cookies.get(c, '')
        if v:
            subject[c] = json.loads(base64.b64decode(v))
    return subject


def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect('pets.db')
    db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(e):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


def init_schema():
    db = get_db()
    c = db.cursor()
    for table in TABLES:
        c.execute('DROP TABLE IF EXISTS ' + table['name'])
        c.execute(table['schema'])
    db.commit()


def pump_db():
    db = get_db()
    c = db.cursor()
    for table in TABLES:
        for row in table['data']:
            insert_object(table['name'], c, row)
    db.commit()


def init_db():
    with app.app_context():
        init_schema()
        pump_db()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_pet(cursor, pet):
    insert_object('pets', cursor, pet)


def insert_object(table, cursor, obj):
    row_keys = sorted(obj.keys())
    keys = '(' + ','.join(row_keys) + ')'
    values = '(' + ','.join(['?'] * len(row_keys)) + ')'
    stmt = 'INSERT INTO {} {} VALUES {}'.format(table, keys, values)
    args = [str(obj[k]) for k in row_keys]
    print str(stmt), args
    cursor.execute(stmt, args)


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


PETS = [{
    'id': '1',
    'name': 'Rufus',
    'owner': 'bob',
    'veterinarian': 'alice',
    'clinic': 'Shady Bluffs',
}, {
    'id': '2',
    'name': 'Sparky',
    'owner': 'bob',
    'veterinarian': 'alice',
    'clinic': 'Shady Bluffs',
}, {
    'id': '3',
    'name': 'Jack',
    'owner': 'john',
    'veterinarian': 'alice',
    'clinic': 'Murky Greens',
}, {
    'id': '4',
    'name': 'Matcha',
    'owner': 'liz',
    'veterinarian': 'alice',
    'clinic': 'Murky Greens',
}, {
    'id': '5',
    'name': 'King',
    'owner': 'liz',
    'veterinarian': 'terry',
    'clinic': 'Murky Greens',
}, {
    'id': '6',
    'name': 'Princess',
    'owner': 'john',
    'veterinarian': 'terry',
    'clinic': 'Murky Greens',
}]

TABLES = [
    {
        'name': 'pets',
        'schema': """CREATE TABLE pets (
                        id TEXT PRIMARY KEY
                        , name TEXT
                        , owner TEXT
                        , veterinarian TEXT
                        , clinic TEXT
                        )""",
        'data': PETS,
    },
]

COOKIES = ['location']

USERS = {
    "bob": {},
    "john": {},
    "liz": {},
    "candace": {},
    "alice": {
        'location': 'Shady Bluffs',
    },
    "terry": {
        'location': 'Murky Greens',
    },
}

if __name__ == '__main__':
    init_db()
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
