import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random

random_generator = Random.new().read


def create_key_pair(size):
    rsa = RSA.generate(size, random_generator)
    private_key = str(rsa.export_key(), 'utf8')
    private_key = private_key.split('-\n')[1].split('\n-')[0]
    public_key = str(rsa.publickey().export_key(), 'utf8')
    public_key = public_key.split('-\n')[1].split('\n-')[0]
    return public_key, private_key


def rsa_encrypt(input_string, public_key):
    rsa_key = RSA.importKey("-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----")
    cipher = PKCS1_v1_5.new(rsa_key)
    return str(base64.b64encode(cipher.encrypt(input_string.encode('utf-8'))), 'utf-8')


def rsa_decrypt(input_string, private_key):
    input_bytes = base64.b64decode(input_string)
    rsa_key = RSA.importKey("-----BEGIN RSA PRIVATE KEY-----\n" + private_key + "\n-----END RSA PRIVATE KEY-----")
    cipher = PKCS1_v1_5.new(rsa_key)
    return str(cipher.decrypt(input_bytes, random_generator), 'utf-8')


if __name__ == '__main__':
    pub, pri = create_key_pair(1024)
    i = rsa_encrypt("123456", pub)
    print(i)
    print(rsa_decrypt(i, pri))
