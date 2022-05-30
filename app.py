from dotenv import load_dotenv
from flask import Flask, request
from flask import jsonify
from flask_bcrypt import Bcrypt
from database import Database
from datetime import datetime
from helper import *
import cloudstorage as gcs
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
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
mysql = MySQL(app)
# Bcrypt encrypt and check support
bcrypt = Bcrypt(app)
logger = Logger()
# New tensor helper with Threshold 0.7
tensorHelper = TensorHelper(0.7)

# Load database from env
db = Database(mysql, os.getenv('MYSQL_DB'))


@app.route("/")
def home():
    """Home Page"""
    return "<h1>Welcome to True Sight</h1>"


@app.route("/api/", methods=['POST'])
def api():
    """API"""
    # Get content type
    content_type = request.headers.get('Content-Type')
    # Only accept application/json content type
    if (content_type == 'application/json'):
        # Get request
        data = request.get_json()

        # Check if key type is available
        if not 'type' in data:
            return jsonify(api_res('failed', 'Invalid api request', '', 0, '', {}))

        # Auth login to get Api key
        if data['type'] == 'auth':
            # Get user with username
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
                        return jsonify(api_res('success', '', 'Auth', 0, 'ApiKey', query_api[0][1]))
                    else:
                        # Generate new api key
                        api_key = generate_key(64)

                        # Save new api key to database
                        db.insert('api_session', {
                            'api_key': api_key, 'user_id': user.id, 'expired': 0})

                        return jsonify(api_res('success', '', 'Auth', 0, 'ApiKey', api_key))

            # Return failed if no matches condition
            return jsonify(api_res('failed', 'Wrong username/password', 'Auth', 0, 'ApiKey', {}))

        # Registration new user
        if data['type'] == 'registration':
            data = dict(data)

            # Validate input
            if data.get('username', None) is None or data.get('password', None) is None or data.get('email', None) is None:
                jsonify(api_res('failed', 'Invalid user input',
                        'Registration', 0, '', {}))

            # Return failed if username is already use
            if len(db.get_where(
                    'users', {'username': data.get('username', None)})) > 0:
                return jsonify(api_res('failed', 'Username already exist', 'Reg', 0, '', {}))

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

            return jsonify(api_res('success', 'User added', 'Registration', 0, '', {}))

        # Search for claim
        if data['type'] == 'search':
            # Return failed if api key is not valid
            if isValidApiKey(request.headers.get('x-api-key', None), db):
                data = dict(data)

                # If no keyword, then return all
                if (data.get('keyword', "") == ""):
                    claims = list()
                    for _ in db.get('claims'):
                        claims.append(Claim.parse(_).get())

                    # Sort by vote from biggest
                    sorted(claims, key=lambda x: (
                        x['upvote']-x['downvote']), reverse=True)

                    return jsonify(api_res('success', '', 'Query', len(claims), "query", claims))

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
                    return jsonify(api_res('success', '', 'Search', len(result), data['keyword'], result[begin:begin+limit]))
                else:
                    # Return nothing if empty
                    return jsonify(api_res('success', 'No result', 'Search', 0, data['keyword'], []))

            else:
                return jsonify(api_res('failed', 'Invalid token', 'Search', 0, '', {}))

        # Predict from given claim
        if data['type'] == 'predict':
            if isValidApiKey(request.headers.get('x-api-key', None), db):
                data = dict(data)

                # Combine title and content
                text_to_predict = data.get('title', '')
                text_to_predict += data.get('content', '')

                # Predict given value
                predicted = predict(text_to_predict, tensorHelper)
                return jsonify(api_res('success', '', 'Predict', 0, 'predict', predicted))

            else:
                # Return failed if api key doesn't exist in database
                return jsonify(api_res('failed', 'Invalid api key', 'Search', 0, '', {}))

        # Return failed if no key 'type' available
        return jsonify(api_res('failed', 'Parameter incorrect', 'Api', 0, '', {}))

    return jsonify(api_res('failed', '', '', 0, '', {}))


@app.route("/api/claim", methods=['POST'])
def addClaim():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        pass


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
