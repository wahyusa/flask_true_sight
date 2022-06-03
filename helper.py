import os
from random import Random
from models.User import User
from models.Claim import Claim
from models.ApiSession import ApiSession
from flask import jsonify
import gcloud as gcs
import string
import base64
import magic
from TrueSightEngine import SearchEngine, TensorHelper, TimeExecution, Logger


def api_res(status: str, message: str, source: str, total: int, dataname: str, data, raw=False):
    """Output API"""
    data = {
        'data': data,
        'dataname': dataname,
        'message': message,
        'source': source,
        'status': status,
        'total': total
    }
    if raw:
        return data
    return jsonify(data)


def invalidRequest():
    return api_res('failed', 'Invalid Content-Type or don\'t have permission', '', 0, '', {})


random = Random()
# Log support
logger = Logger()


def voteToJson(vote: str):
    return{
        'id': int(vote.split(':')[0]),
        'value': int(vote.split(':')[1])
    }


def userToProfileJson(user: User, hidePresonalInformation: bool = True):
    if hidePresonalInformation:
        # Do not send personal information
        votes = None
        bookmarks = None
        date_created = None
        email = None
    else:
        # Send personal information
        bookmarks = None if user.bookmarks is None else [int(x) for x in user.bookmarks.split(
            ',')]
        votes = None if user.votes is None else [voteToJson(x) for x in user.votes.split(
            ',')]
        date_created = user.date_created
        email = user.email
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": email,
        "bookmarks": bookmarks,
        "date_created": date_created,
        "avatar": user.avatar,
        "verified": user.verified,
        "votes": votes
    }


def uploader(bytes, destination: str) -> bool:
    logger.debug('Request upload file')
    destination = destination.strip()
    if any(destination.lower().endswith(x) for x in os.environ.get('UPLOAD_ALLOWED_EXSTENSION', '.jpg;.jpeg;.png;.bmp').split(';')):
        if int(os.environ.get("LOCAL", 0)) == 1:
            full_path = os.path.join(os.getcwd(), destination)
            if not os.path.exists(os.path.dirname(destination)):
                os.mkdir(os.path.dirname(destination))
            with open(full_path, 'wb') as uploadfile:
                uploadfile.write(bytes)
            logger.debug('File upload to "' + full_path + '"')
        else:
            full_path = "gs://{}/uploads/{}".format(
                os.getenv('BUCKET_NAME'), destination)
            with gcs.getBlob(full_path).open('wb') as uploadfile:
                uploadfile.write(bytes)
            logger.debug('File upload to "' + full_path + '"')
    else:
        raise Exception('Extension not Allowed')

def deletefromresource(destination: str) -> bool:
    logger.debug('Request delete file')
    destination = destination.strip()
    if int(os.environ.get("LOCAL", 0)) == 1:
        full_path = os.path.join(os.getcwd(), destination)
        if os.path.exists(os.path.dirname(destination)):
            os.remove(destination)
        else:
            logger.error("Delete Resource",'File not found "' + full_path + '"')
    else:
        full_path = "gs://{}/uploads/{}".format(
            os.getenv('BUCKET_NAME'), destination)
        gcs.getBlob(full_path).delete()

def predict(claim: str, tensorhelper: TensorHelper):
    """Predict from string"""
    try:
        # Remove any stopwords
        claim = ' '.join(SearchEngine.RemoveStopWords(
            claim.replace('\n', ' ').split()))

        logger.debug("Started Prediction")
        if not tensorhelper.is_model_loaded:
            logger.debug("Loaded Tensor Model")
            if int(os.environ.get("LOCAL", 0)) == 1:
                # Loaded Tensor Model
                tensorhelper.openModel(
                    '/home/rvinz/Documents/Github/tensor_model/indobert-base-p1-87')
                logger.debug("Loaded Tokenizer")
                # Loaded Tokenizer
                tensorhelper.loadTokenizer(
                    '/home/rvinz/Documents/Github/tensor_model/indobert-base-p1-tokenizer-87.pickle')
            else:
                # Loaded Tensor Model
                tensorhelper.openModel(os.environ.get('MODEL_PATH'))
                logger.debug("Loaded Tokenizer")
                # Loaded Tokenizer
                tensorhelper.loadTokenizer(os.environ.get('TOKENIZER_PATH'))
        predicted = tensorhelper.predict_claim(claim, 60)
        predicted['val_prediction'] = str(predicted['val_prediction'])
        predicted['prediction'] = str(predicted['prediction'])
        logger.debug("Finished Prediction")
        return predicted
    except Exception as ex:
        logger.error("Predict", ex)


def isValidApiKey(api_key: str, db) -> bool:
    """Check is valid api key"""
    # Check is api key exist in database
    result = db.get_where('api_session', {'api_key': api_key})
    if (len(result) > 0):
        return True
    return False


def checkValidAPIrequest(request, db, allow_no_apikey=False, content_type=['application/json', 'multipart/form-data', 'application/x-www-form-urlencoded']) -> bool:
    # check if content type is equal
    if content_type is None:
        if allow_no_apikey:
            return True
        else:
            # check if api key is valid
            return isValidApiKey(request.headers.get('x-api-key', None), db)
    elif any(request.headers.get('Content-Type', 'NULL').startswith(x) for x in content_type):
        if allow_no_apikey:
            return True
        else:
            # check if api key is valid
            return isValidApiKey(request.headers.get('x-api-key', None), db)
    else:
        return False


def invalidUserInput(source: str):
    return api_res('failed', 'Invalid user input, some required fields do not exist',  source, 0, '', {})


def getUserFromApiKey(api_key: str, db) -> User:
    """Get User from api key"""
    if api_key is None:
        return None
    # Check is api key exist in database
    result = db.get_where('api_session', {'api_key': api_key})
    if (len(result) > 0):
        # Get first user from result
        # result field 0: id, 1: api_key, 2: user_id, 3: expired_date
        user = User.parse(db.get_where(
            'users', {'id': result[0][2]})[0])
        return user
    return None


def generate_key(length):
    """Generate random alfanum with given length"""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
