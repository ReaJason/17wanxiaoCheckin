import hashlib


def sha256(string):
    sha1_object = hashlib.sha256()
    sha1_object.update(str(string))
    return sha1_object.hexdigest()