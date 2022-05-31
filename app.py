from helper import *
from dotenv import load_dotenv
from flask import Flask, request
from flask_bcrypt import Bcrypt
from database import Database
from datetime import datetime
import os

# from google.appengine.api import app_identity

# Code from https://cloud.google.com/appengine/docs/standard/python/googlecloudstorageclient/read-write-to-cloud-storage
# def get(self):
#   bucket_name = os.environ.get('BUCKET_NAME',
#                                app_identity.get_default_gcs_bucket_name())

#   self.response.headers['Content-Type'] = 'text/plain'
#   self.response.write('Demo GCS Application running from Version: '
#                       + os.environ['CURRENT_VERSION_ID'] + '\n')
#   self.response.write('Using bucket name: ' + bucket_name + '\n\n')

load_dotenv()

app = Flask(__name__)
# Bcrypt encrypt and check support
bcrypt = Bcrypt(app)
logger = Logger()
# New tensor helper with Threshold 0.7
tensorHelper = TensorHelper(0.7)

# Use 127.0.0.1 if running in cloud instead of using sql public api
db_host = "127.0.0.1" if int(os.environ.get(
    'LOCAL', 0)) == 0 else os.environ.get('INSTANCE_HOST', '127.0.0.1')

# Load database from env
global db
db = Database(db_host, os.getenv('DB_USER'),
              os.getenv('DB_PASS'), os.getenv('DB_NAME'), os.getenv('INSTANCE_CONNECTION_NAME'), int(os.environ.get('LOCAL', 0)))


@app.route("/")
def home():
    """Home Page"""
    return "<h1>Welcome to True Sight</h1>"


@app.route("/api/", methods=['POST'])
def api():
    """API"""
    return "Welcome to True Sight API"


@app.route("/api/auth", methods=['POST'])
def auth():
    # Check is valid request and allow without api key
    if checkValidAPIrequest(request, db, allow_no_apikey=True):
        data: dict = dict(request.get_json())
        if (any(x in data for x in ['username', 'password'])):
            # Query users where username matched input
            user = db.get_where(
                'users', {'username': data['username']})

            if len(user) > 0:
                # Cast to User()
                user = User.parse(user[0])

                # Check if given password match with user password
                if bcrypt.check_password_hash(user.password, data['password']):
                    # Get api key from database
                    query_api = db.get_where(
                        'api_session', {'user_id': user.id})

                    logger.info('Auth', 'User login ' + user.username)

                    if len(query_api) > 0:
                        # If exist then return api key
                        return api_res('success', '', 'Auth', 0, 'ApiKey', query_api[0][1])
                    else:
                        # Generate new api key
                        api_key = generate_key(64)

                        # Save new api key to database
                        db.insert('api_session', {
                            'api_key': api_key, 'user_id': user.id, 'expired': 0})

                        return api_res('success', '', 'Auth', 0, 'ApiKey', api_key)

            # Return failed if no matches condition
            return api_res('failed', 'Wrong username/password', 'Auth', 0, 'ApiKey', {})
        else:
            # Return if no needed field in request
            return invalidUserInput('Auth')
    else:
        return invalidRequest()


@app.route("/api/registration", methods=['POST'])
def reqistration():
    # Check is valid request and allow without api key
    if checkValidAPIrequest(request, db, allow_no_apikey=True):
        data: dict = dict(request.get_json())
        # Validate input
        if (any(x in data for x in ['username', 'email', 'password'])):
            return invalidUserInput('Registration')

        # Return failed if username is already use
        if len(db.get_where(
                'users', {'username': data.get('username', None)})) > 0:
            return api_res('failed', 'Username already exist', 'Reg', 0, '', {})

        # Insert new user into database
        db.insert('users', User().set(
            None,
            data.get('username', None),
            data.get('email', None),
            bcrypt.generate_password_hash(data.get('password', None)),
            datetime.now().timestamp()
        ).get())

        logger.info('Registration', 'User created ' + data['username'])

        # Get user from database to get id
        user = User.parse(db.get_where(
            'users', {'username': data['username']})[0])

        # Generate new api key and insert into table
        api_key = generate_key(64)
        db.insert('api_session', {
            'api_key': api_key, 'user_id': user.id, 'expired': 0})

        return api_res('success', 'User added', 'Registration', 0, '', {})
    else:
        return invalidRequest()


@app.route("/api/search", methods=['POST'])
def search_api():
    if checkValidAPIrequest(request, db):
        data: dict = dict(request.get_json())

        # If no keyword, then return all
        if (data.get('keyword', "") == ""):
            claims = list()
            for _ in db.get('claims'):
                claims.append(Claim.parse(_).get())

            # Sort by vote from biggest
            sorted(claims, key=lambda x: (
                x['upvote']-x['downvote']), reverse=True)

            return api_res('success', '', 'Query', len(claims), "query", claims)

        # If has keywords, get claims from database and build array dictionary
        claims = {}
        for _ in db.get('claims'):
            claim = Claim.parse(_).get()
            claims = SearchEngine.addDataToDictionary(claim, claims)

        # Cut data from given index and limit
        begin = data.get('begin', 0)
        limit = data.get('limit', 99999)

        if len(claims.values()) > 0:
            # Search data by given keywords
            result = SearchEngine.search_from_dict(data['keyword'], claims, [
                'title', 'description'])
            return api_res('success', '', 'Search', len(result), data['keyword'], result[begin:begin+limit])
        else:
            # Return nothing if empty
            return api_res('success', 'No result', 'Search', 0, data['keyword'], [])
    else:
        return invalidRequest()


@app.route("/api/predict", methods=['POST'])
def predict_api():
    if checkValidAPIrequest(request, db):
        data: dict = dict(request.get_json())

        # Combine title and content
        text_to_predict = data.get('title', '')
        text_to_predict += data.get('content', '')

        # Predict given value
        predicted = predict(text_to_predict, tensorHelper)
        return api_res('success', '', 'Predict', 0, 'predict', predicted)
    else:
        return invalidRequest()


@app.route("/api/profile", methods=['POST'])
def profile_api():
    if checkValidAPIrequest(request, db):
        data: dict = dict(request.get_json())
        if (any(x in data for x in ['id'])):
            return invalidUserInput('Profile')
    else:
        return invalidRequest()


@app.route("/api/claim", methods=['POST'])
def claim_api():
    if checkValidAPIrequest(request, db):
        data: dict = dict(request.get_json())
        if (any(x in data for x in ['id'])):
            return invalidUserInput('Claim')

    else:
        return invalidRequest()


@app.route('/uploads/<path>')
def get_resources(path):
    print(path)


if __name__ == '__main__':
    server_port = os.environ.get('FLASK_RUN_PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
