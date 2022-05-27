from random import Random
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask, request
from flask import jsonify
import os
import string
from models.User import User
from database import Database
from datetime import datetime

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

db = Database(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USERNAME'),
    password=os.getenv('MYSQL_PASS'),
    database=os.getenv('MYSQL_DATABASE')
)

# mycursor = mydb.cursor()
# sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# val = ("John", "Highway 21")
# mycursor.execute(sql, val)
# mydb.commit()

# mycursor = mydb.cursor()
# mycursor.execute("SELECT * FROM customers")
# myresult = mycursor.fetchall()
# for x in myresult:
#   print(x)

# hashVar = <bcrypt object>.generate_password_hash('< password to hash >')
# hashVar = <bcrypt object>.generate_password_hash('< password to hash >') .decode(‘utf-8’)


def api_res(status: str, message: str, source: str, total: int, dataname: str, data):
    return {
        'data': data,
        'dataname': dataname,
        'message': message,
        'source': source,
        'status': status,
        'total': total
    }


random = Random()


def generate_key(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


@app.route("/")
def home():
    return "<h1>Welcome to True Sight</h1>"


@app.route("/api/", methods=['POST'])
def api():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = request.get_json()
        if not 'type' in data:
            return jsonify(api_res('failed', 'Invalid api request', '', 0, '', {}))
        if data['type'] == 'auth':
            user = db.get_where(
                'users', {'username': data['username']})
            if len(user) > 0:
                print(user[0])
                user = User.parse(user[0])
                print(user.password)
                if bcrypt.check_password_hash(user.password, data['password']):
                    query_api = db.get_where(
                        'api_session', {'user_id': user.id})
                    if len(query_api) > 0:
                        return jsonify(api_res('success', '', 'Auth', 0, 'ApiKey', query_api[0][1]))

        if data['type'] == 'registration':
            if len(db.get_where(
                    'users', {'username': data['username']})) > 0:
                return jsonify(api_res('failed', 'Username already exist', 'Reg', 0, '', {}))

            db.insert('users', User().set(
                None,
                data['username'],
                data['email'],
                bcrypt.generate_password_hash(data['password']),
                datetime.now().timestamp()
            ).get())
            user = User.parse(db.get_where(
                'users', {'username': data['username']})[0])
            api_key = generate_key(64)
            db.insert('api_session', {
                'api_key': api_key, 'user_id': user.id, 'expired': 0})

            return jsonify(api_res('success', 'User added', 'Registration', 0, '', {}))

        if data['type'] == 'query':
            if len(db.get_where(
                    'users', {'username': data['username']})) > 0:
                return jsonify(api_res('failed', 'Username already exist', 'Reg', 0, '', {}))

            db.insert('users', User().set(
                None,
                data['username'],
                data['email'],
                bcrypt.generate_password_hash(data['password']),
                datetime.now().timestamp()
            ).get())
            user = User.parse(db.get_where(
                'users', {'username': data['username']})[0])
            api_key = generate_key(64)
            db.insert('api_session', {
                'api_key': api_key, 'user_id': user.id, 'expired': 0})

            return jsonify(api_res('success', 'User added', 'Registration', 0, '', {}))

        return jsonify(api_res('failed', 'Parameter incorrect', 'Api', 0, '', {}))

    return jsonify(api_res('failed', '', '', 0, '', {}))
