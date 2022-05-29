import os
from random import Random
from models.User import User
from models.Claim import Claim
import cloudstorage as gcs
import string
import base64
from TrueSightEngine import SearchEngine, TensorHelper, TimeExecution, Logger
import magic

# Disable GPU for TensorFlow and BertTokenizer
mime = magic.Magic(mime=True)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def api_res(status: str, message: str, source: str, total: int, dataname: str, data):
    """Output API"""
    return {
        'data': data,
        'dataname': dataname,
        'message': message,
        'source': source,
        'status': status,
        'total': total
    }


random = Random()
# Log support
logger = Logger()


def addAttachment(source, dest, filename: str):
    bytes_data = base64.b64decode(source)
    file_mime_type = mime.from_buffer(bytes_data)
    if file_mime_type == "image/jpeg":
        os.mkdir(os.path.join(os.getcwd(), dest))
        if not filename.lower().endswith('.jpg'):
            filename += '.jpg'
        upload_file = gcs.open(os.path.join(os.getcwd(), dest, filename), "wb")
        upload_file.write(bytes_data)
        upload_file.close()


def predict(claim, tensorhelper: TensorHelper):
    """Predict from string"""

    try:
        logger.debug("Started Prediction")
        if not tensorhelper.is_model_loaded:
            logger.debug("Loaded Tensor Model")
            tensorhelper.openModel(os.path.join(
                os.getcwd(), 'tensor_model', 'indobert-base-p1-87'))
            logger.debug("Loaded Tokenizer")
            tensorhelper.loadTokenizer(os.path.join(
                os.getcwd(), 'tensor_model', 'indobert-base-p1-tokenizer-87.pickle'))
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
