from google.cloud import storage
from google.cloud.client import Client
import re


def getBlob(path: str) -> storage.Blob:
    client = storage.Client()
    # Load from Google Cloud Storage
    pattern = r"^gs:\/\/([A-Za-z0-9-]+)((?:\/[^\/]+)+)\/?$"
    matches = re.match(pattern, path)
    if (not matches is None):
        bucket_name = matches.groups()[0]
        bucket = client.get_bucket(bucket_name)
        file_path = matches.groups()[1][1:]
        blob = bucket.blob(file_path)
    else:
        raise Exception("Not valid Google Cloud File Path")
    return blob


def isGoogleCloudPath(path: str) -> bool:
    pattern = r"^gs:\/\/([A-Za-z0-9-]+)((?:\/[^\/]+)*)\/?$"
    matches = re.match(pattern, path)
    if (matches is None):
        return False
    else:
        return True


def getBucketNameFromPath(path: str) -> str:
    pattern = r"^gs:\/\/([A-Za-z0-9-]+)"
    matches = re.match(pattern, path)
    return matches.groups()[0][1:]


def isFolder(path: str) -> bool:
    c = Client()

    text = getBlob('gs://truesight-bucket/test_folder')
    print(text)
    return False
