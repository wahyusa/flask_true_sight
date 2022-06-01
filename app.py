from werkzeug.routing import BaseConverter
from helper import *
from dotenv import load_dotenv
from flask import Flask, request, abort, json
from flask_bcrypt import Bcrypt
from database import Database
from datetime import datetime
import gcloud as gcs
import os
import magic
import re


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
if not 'tensorHelper' in locals():
    global tensorHelper
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


@app.route("/api")
def api():
    """API"""
    return "Welcome to True Sight API"


def convert_request(request):
    if request.headers.get('Content-Type') == 'application/json':
        return dict(request.get_json())
    else:
        return dict(request.form)


@app.route("/api/auth/", methods=['POST'])
def auth():
    # Check is valid request and allow without api key
    if checkValidAPIrequest(request, db, allow_no_apikey=True):
        data: dict = convert_request(request)
        if all(x in data for x in ['username', 'password']):
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
                            'api_key': api_key, 'user_id': user.id, 'date_created': datetime.now().timestamp(), 'expired': 0})

                        return api_res('success', '', 'Auth', 0, 'ApiKey', api_key)

            # Return failed if no matches condition
            return api_res('failed', 'Wrong username/password', 'Auth', 0, 'ApiKey', [])
        else:
            # Return if no needed field in request
            return invalidUserInput('Auth')
    else:
        return invalidRequest()


@app.route("/api/registration/", methods=['POST'])
def reqistration():
    # Check is valid request and allow without api key
    if checkValidAPIrequest(request, db, allow_no_apikey=True):
        data: dict = convert_request(request)
        # Validate input
        if not all(x in data for x in ['username', 'email', 'password']):
            return invalidUserInput('Registration')

        # Return failed if username is already use
        if len(db.get_where(
                'users', {'username': data.get('username', None)})) > 0:
            return api_res('failed', 'Username already exist', 'Reg', 0, '', [])

        # Insert new user into database
        db.insert('users', User().set(
            None,
            data.get('username', None),
            data.get('full_name', data.get('username')),
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
            'api_key': api_key, 'user_id': user.id, 'date_created': datetime.now().timestamp(), 'expired': 0})

        return api_res('success', 'User added', 'Registration', 0, '', [])
    else:
        return invalidRequest()


@app.route("/api/search/", methods=['POST'])
def search_api():
    if checkValidAPIrequest(request, db):
        data: dict = convert_request(request)

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


@app.route("/api/predict/", methods=['POST'])
def predict_api():
    if checkValidAPIrequest(request, db):
        data: dict = convert_request(request)

        # Combine title and content
        text_to_predict = data.get('title', '')
        text_to_predict += data.get('content', '')

        # Predict given value
        predicted = predict(text_to_predict, tensorHelper)
        return jsonify(predicted)
    else:
        return invalidRequest()


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


@app.route('/uploads/<regex(".*"):path>')
def get_resources(path):
    if not request.args.get('id', None) is None:
        logger.debug('ID: ' + request.args.get('id'))

    # Get parent folder
    dirName = path.split('/')[0].lower()

    # MimeType Exception
    mime_exception = ['html', 'javascript',
                      'octet-stream']

    # If parent folder is claim
    if dirName == 'claim':
        if int(os.environ.get('LOCAL', 0)) == 1:
            # Build full path
            full_path = os.path.join(os.getcwd(), path)

            # Only if file exists
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # Open file and read all bytes
                file_stream = open(full_path, 'rb').read()
                logger.debug('File Read:' + full_path)
                # Get mime_type of file
                mime_type = magic.from_buffer(file_stream)
                if any(x in mime_type.lower() for x in mime_exception):
                    mime_type = str("text/plain")
                logger.debug('File Type:' + mime_type)
                # Make response
                response = app.response_class(
                    response=file_stream,
                    mimetype=mime_type
                )
                # Return response
                return response
            else:
                # If file not exists return 404
                return abort(404)
        else:
            # Build full cloud storage path
            full_path = "gs://" + \
                os.getenv("BUCKET_NAME") + "/uploads/" + path

            # Check File if exists
            if gcs.isFileExist(full_path):
                # Open file and read all bytes
                file_stream = gcs.getBlob(full_path).open('rb').read()
                logger.debug('File Read:' + full_path)
                # Get mime type
                mime_type = magic.from_buffer(file_stream)
                if any(x in mime_type.lower() for x in mime_exception):
                    mime_type = str("text/plain")
                logger.debug('File Type:' + mime_type)
                # Make Response
                response = app.response_class(
                    response=file_stream,
                    mimetype=mime_type
                )
                # Return response
                return response
            else:
                # If file not exists return 404
                return abort(404)
    elif dirName == 'avatar':
        if checkValidAPIrequest(request, db, content_type=None):
            paths_split = path.split('/')
            # Check is have sub directory or file
            if not len(paths_split) > 1:
                return abort(404)
            # Get Current user depends on api key
            current_user: User = getUserFromApiKey(
                request.headers.get('x-api-key', None), db)
            logger.debug(
                f"User {current_user.username}({str(current_user.id)}) access avatar.")
            if int(os.environ.get('LOCAL', 0)) == 1:
                # Build full path
                full_path = os.path.join(
                    os.getcwd(), 'avatar', str(current_user.id), os.pathsep.join(paths_split[1:]))

                # Only if file exists
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    # Open file and read all bytes
                    file_stream = open(full_path, 'rb').read()
                    logger.debug('File Read:' + full_path)
                    # Get mime_type of file
                    mime_type = magic.from_buffer(file_stream)
                    if any(x in mime_type.lower() for x in mime_exception):
                        mime_type = str("text/plain")
                    logger.debug('File Type:' + mime_type)
                    # Make response
                    response = app.response_class(
                        response=file_stream,
                        mimetype=mime_type
                    )
                    # Return response
                    return response
                else:
                    # If file not exists return 404
                    return abort(404)
            else:
                # Build full cloud storage path
                full_path = "gs://" + \
                    os.getenv("BUCKET_NAME") + "/uploads/avatar/" + \
                    str(current_user.id) + '/' + \
                    os.pathsep.join(paths_split[1:])

                # Check File if exists
                if gcs.isFileExist(full_path):
                    # Open file and read all bytes
                    file_stream = gcs.getBlob(full_path).open('rb').read()
                    logger.debug('File Read:' + full_path)
                    # Get mime type
                    mime_type = magic.from_buffer(file_stream)
                    # Avoid file execution
                    if any(x in mime_type.lower() for x in mime_exception):
                        mime_type = str("text/plain")
                    logger.debug('File Type:' + mime_type)
                    # Make Response
                    response = app.response_class(
                        response=file_stream,
                        mimetype=mime_type
                    )
                    # Return response
                    return response
                else:
                    # If file not exists return 404
                    return abort(404)
        else:
            # Return Forbidden
            return abort(403)
    else:
        # If file not exists return 404
        return abort(404)


@app.route("/api/get/profile/", methods=['POST'])
def get_profile():
    if checkValidAPIrequest(request, db):
        data: dict = convert_request(request)
        current_user: User = getUserFromApiKey(
            request.headers.get('x-api-key', None), db)
        if all(x in data for x in ['id']):
            profiles = db.get_where('users', {'id': data['id']})
            if (len(profiles) > 0):
                profil: User = User.parse(profiles[0])
                if profil.id == current_user.id:
                    return api_res('success', 'Own Profile', 'Get Profile', 0, 'profile', userToProfileJson(profil, hidePresonalInformation=False))
                else:
                    return api_res('success', '', 'Get Profile', 0, 'profile', userToProfileJson(profil))
            else:
                respon = app.response_class(
                    response=json.dumps('User doesn\'t exist'),
                    status=406,
                    mimetype='application/json'
                )
                return respon
        else:
            return invalidUserInput('Get Profile')
    else:
        return invalidRequest()


@app.route("/api/get/claim/", methods=['POST'])
def get_claim():
    if checkValidAPIrequest(request, db):
        data: dict = convert_request(request)
        if all(x in data for x in ['id']):
            claims = db.get_where('claims', {'id': data['id']})
            if (len(claims) > 0):
                claim: Claim = Claim.parse(claims[0])
                return api_res('success', '', 'Claim', 0, 'claim', claim.get())
            else:
                respon = app.make_response("ss")
                respon.status_code = 406
                respon.headers.remove('Content-Type')
                respon.headers.add('Content-Type', 'application/json')
                return respon
        else:
            return invalidUserInput('Get Claim')

    else:
        return invalidRequest()


@app.route("/api/set/profile/", methods=['POST'])
def set_profile():
    if checkValidAPIrequest(request, db, content_type=['multipart/form-data']):
        data: dict = convert_request(request)
        if any(x in data for x in ['email', 'full_name']) or 'avatar' in request.files:
            current_user: User = getUserFromApiKey(
                request.headers.get('x-api-key', None), db)
            current_user.email = data.get('email', current_user.email)
            current_user.full_name = data.get(
                'full_name', current_user.full_name)
            db.update_where('users', current_user.get(),
                            {'id': current_user.id})
            if 'avatar' in request.files:
                avatar = request.files.get('avatar')
                if avatar.content_length > 5242880:
                    return api_res('failed', 'File size is too big', 'Profile', 0, 'avatar', [])
                try:
                    if '.' in avatar.filename:
                        uploader(avatar.stream.read(), 'avatar/' +
                                 current_user.id + "." + avatar.filename.split('.')[-1])
                    else:
                        raise Exception('Extension not allowed')
                except Exception as ex:
                    return api_res('failed', ex, 'Profile', 0, 'avatar', [])
            return api_res('success', "", 'Profile', 0, '', [])
        else:
            return invalidUserInput('Set Profile')
    else:
        return invalidRequest()


@app.route("/api/set/claim/", methods=['POST'])
def set_claim():
    if checkValidAPIrequest(request, db, content_type=['multipart/form-data']):
        data: dict = convert_request(request)
        if any(x in data for x in ['title', 'description', 'fake', 'url']) and 'id' in data:
            current_user: User = getUserFromApiKey(
                request.headers.get('x-api-key', None), db)
            claim = Claim.parse(db.get_where(
                'claims', {'id': data.get('id')})[0])
            if claim.author_id == current_user.id:
                claim.title = data.get('title', claim.title)
                claim.description = data.get('title', claim.description)
                claim.fake = data.get('title', claim.fake)
                claim.url = data.get('title', claim.url)
                attachmentUrl = list()
                for _, file in request.files.items():
                    if file.content_length > 5242880:
                        return api_res('failed', 'File size is too big', 'Attachment', 0, file.name, [])
                    try:
                        uploader(file.stream.read(), 'claim/' +
                                 claim.id + "/" + file.name)
                        attachmentUrl.append(os.getenv('BASE_URL') + 'claim/' +
                                             claim.id + "/" + file.name)
                    except Exception as ex:
                        return api_res('failed', ex, 'Attachment', 0, file.name, [])

                if len(attachmentUrl) > 0:
                    claim.attachment = ','.join(attachmentUrl)

                db.update_where('claims', claim.get(), {'id': claim.id})
                return api_res('success', "", 'Claim', 0, '', [])
            else:
                return abort(403)
        else:
            return invalidUserInput('Set Claim')

    else:
        return invalidRequest()


@app.route("/test/")
def test():
    pass


@app.route("/api/create/claim/", methods=['POST'])
def create_claim():
    if checkValidAPIrequest(request, db, content_type=['multipart/form-data']):
        data: dict = convert_request(request)
        if all(x in data for x in ['title', 'description', 'fake']):
            current_user: User = getUserFromApiKey(
                request.headers.get('x-api-key', None), db)
            claim = Claim().set(
                id=None,
                title=data.get('title'),
                description=data.get('description'),
                author_id=current_user.id,
                attachment="",
                comment_id=0,
                date_created=datetime.now().timestamp(),
                fake=data.get('fake'),
                url=data.get('url', '')
            )

            attachmentUrl = list()
            for _, file in request.files.items():
                if file.content_length > 5242880:
                    return api_res('failed', 'file to large', 'Attachment', 0, file.name, [])
                try:
                    uploader(file.stream.read(), 'claim/' +
                             claim.id + "/" + file.name)
                    attachmentUrl.append(os.getenv('BASE_URL') + 'claim/' +
                                         claim.id + "/" + file.name)
                except Exception as ex:
                    return api_res('failed', ex, 'Attachment', 0, file.name, [])

            if len(attachmentUrl) > 0:
                claim.attachment = ','.join(attachmentUrl)

            db.insert('claims', claim.get())
            return api_res('success', "", 'Claim', 0, '', [])
        else:
            return invalidUserInput('Create Claim')
    else:
        return invalidRequest()


if __name__ == '__main__':
    server_port = os.environ.get('FLASK_RUN_PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
