from google.cloud import storage
import re


def getBlob(path: str) -> storage.Blob:
    client = storage.Client()
    # Load from Google Cloud Storage
    pattern = r"^gs:\/\/([A-Za-z0-9-]+)((?:\/[^\/]+)+)\/?$"
    matches = re.match(pattern, path)
    if (not matches is None):
        bucket_name = matches.groups[1]
        bucket = client.get_bucket(bucket_name)
        file_path = matches.groups[2]
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
    return matches.groups[1]
