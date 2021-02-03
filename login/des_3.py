from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
import base64, json


def des_3_encrypt(string, key, iv):
    cipher = DES3.new(key, DES3.MODE_CBC, iv.encode("utf-8"))
    ct_bytes = cipher.encrypt(pad(string.encode('utf8'), DES3.block_size))
    ct = base64.b64encode(ct_bytes).decode('utf8')
    return ct


def des_3_decode(string, key, iv):
    ct = base64.b64decode(string)
    cipher = DES3.new(key.encode('utf-8'), DES3.MODE_CBC, iv.encode('utf-8'))
    pt = unpad(cipher.decrypt(ct), DES3.block_size)
    return pt


def object_encrypt(object_to_encrypt, key, iv="66666666"):
    return des_3_encrypt(json.dumps(object_to_encrypt), key, iv)


def object_decrypt(string, key, iv="66666666"):
    string = string.replace('\n', '')
    return json.loads(des_3_decode(string, key, iv))
