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
    return matches.groups()[0]


def getPathWithoutBucket(path: str) -> str:
    # Load from Google Cloud Storage
    pattern = r"^gs:\/\/([A-Za-z0-9-]+)((?:\/[^\/]+)+)\/?$"
    matches = re.match(pattern, path)
    if (not matches is None):
        return matches.groups()[1][1:]
    else:
        return None


def isFolderExist(path: str) -> bool:
    if path.endswith('/'):
        return getBlob(path).exists()
    else:
        return getBlob(path + '/').exists()


def getBlobs(dir: str) -> list:
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    bucket_name = getBucketNameFromPath(dir)
    blobs = storage_client.list_blobs(bucket_name)
    files = list()
    for blob in blobs:
        if blob.name.startswith(getPathWithoutBucket(dir)) and not blob.name == getPathWithoutBucket(dir):
            files.append(blob)
    return files


def isFileExist(path: str) -> bool:
    if path.endswith('/'):
        return False
    else:
        return getBlob(path).exists()
