import os
from random import Random
from models.User import User
from models.Claim import Claim
from flask import jsonify
import gcloud as gcs
import string
import base64
from TrueSightEngine import SearchEngine, TensorHelper, TimeExecution, Logger
import magic


def api_res(status: str, message: str, source: str, total: int, dataname: str, data):
    """Output API"""
    return jsonify({
        'data': data,
        'dataname': dataname,
        'message': message,
        'source': source,
        'status': status,
        'total': total
    })


def invalidRequest():
    return api_res('failed', 'Invalid Request or access denied', '', 0, '', {})


random = Random()
# Log support
logger = Logger()


def addAttachment(source, dest, filename: str):
    mime = magic
    bytes_data = base64.b64decode(source)
    file_mime_type = mime.from_buffer(bytes_data)
    if file_mime_type == "image/jpeg":
        os.mkdir(os.path.join(os.getcwd(), dest))
        if not filename.lower().endswith('.jpg'):
            filename += '.jpg'
        upload_file = gcs.getBlob(filename).open("wb")
        upload_file.write(bytes_data)
        upload_file.close()


def getMime(filename):
    mime = magic
    bytes_data = open(filename).buffer
    file_mime_type = mime.from_buffer(bytes_data)
    return file_mime_type


def predict(claim, tensorhelper: TensorHelper):
    """Predict from string"""

    try:
        logger.debug("Started Prediction")
        if not tensorhelper.is_model_loaded:
            logger.debug("Loaded Tensor Model")
            if int(os.environ.get("LOCAL", 0)) == 1:
                tensorhelper.openModel(
                    '/home/rvinz/Documents/Github/tensor_model/indobert-base-p1-87')
                logger.debug("Loaded Tokenizer")
                tensorhelper.loadTokenizer(
                    '/home/rvinz/Documents/Github/tensor_model/indobert-base-p1-tokenizer-87.pickle')
            else:
                tensorhelper.openModel(os.environ.get('MODEL_PATH'))
                logger.debug("Loaded Tokenizer")
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


def checkValidAPIrequest(request, db, allow_no_apikey=False, content_type='application/json') -> bool:
    # check if content type is equal
    if request.headers.get('Content-Type') == content_type:
        if allow_no_apikey:
            return True
        else:
            # check if api key is valid
            return isValidApiKey(request.headers.get('x-api-key', None), db)
    else:
        if allow_no_apikey:
            return True
        else:
            # check if api key is valid
            return isValidApiKey(request.headers.get('x-api-key', None), db)


def invalidUserInput(source: str):
    return jsonify(api_res('failed', 'Invalid user input',  source, 0, '', {}))


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
