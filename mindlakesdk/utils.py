from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Signature import pss
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256, HMAC
from Crypto.Random import get_random_bytes
from enum import Enum
import requests
import json
import mindlakesdk.settings as settings
import logging

class ResultType:
    def __init__(self, code: int, message: str = None, data = None):
        self.code = code
        self.message = message
        self.data = data
        
    def __bool__(self):
        return self.code == 0
    
class DataType(Enum):
    int4 = 1
    int8 = 2
    float4 = 3
    float8 = 4
    decimal = 5
    text = 6
    timestamp = 7

class Session:
    def __init__(self) -> None:
        self.walletAddress = None
        self.isRegistered = False
        self.mk = None
        self.sk = None
        self.isLogin = False
        self.token = None
        self.accountID = None
        self.nodePK = None
        self.pkID = None
        self.appKey = None
        self.gateway = None
        
def genRSAKey():
    rsaKey = RSA.generate(2048)
    return rsaKey

def genAESKey():
    aesKey = get_random_bytes(16)
    return aesKey

def sha256Hash(data):
    h = SHA256.new(data)
    return h.digest()

def aesEncrypt(key, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data, AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return encrypted_data

def aesDecrypt(key, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(data)
    result = unpad(decrypted_data, AES.block_size)
    return result

def aesGCMEncrypt(key, iv, data):
    cipher = AES.new(key, AES.MODE_GCM, iv)
    encrypted_data, tag = cipher.encrypt_and_digest(data)
    return tag + encrypted_data

def aesGCMDecrypt(key, iv, data, tag):
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_data = cipher.decrypt_and_verify(data, tag)
    return decrypted_data

def hmacHash(key, data):
    h = HMAC.new(key, digestmod=SHA256)
    h.update(data)
    return h.digest()

def rsaEncrypt(pubKey, data):
    public_key = RSA.import_key(pubKey)
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data

def rsaDecrypt(priKey, data):
    private_key = RSA.import_key(priKey)
    cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data

def rsaSign(priKey: RSA.RsaKey, data: bytes) -> bytes:
    # private_key = RSA.import_key(priKey)
    h = SHA256.new(data)
    signature = pss.new(priKey).sign(h)
    return signature

def rsaVerify(pubKey, data, signature):
    public_key = RSA.import_key(pubKey)
    h = SHA256.new(data)
    verifier = pss.new(public_key)
    try:
        verifier.verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False
    
def request(data, session: Session):
    headers = {}
    headers['Content-Type'] = 'application/json'
    headers['wa'] = session.walletAddress
    headers['ver'] = settings.VERSION
    headers['app'] = session.appKey
    if session.token:
        headers['token'] = session.token
    response = requests.post(session.gateway, json=data, headers=headers)
    logging.debug("============== Mind SDK request ==============")
    logging.debug('MindSDKHeaders: %s'%headers)
    logging.debug("MindSDKData: %s"%data)
    logging.debug('MindSDKRequest: %s'%response.request.body.decode('utf-8'))
    logging.debug('MindSDKResponse: %s'%response.text)
    if response and response.status_code == 200:
        return json.loads(response.text)
    else:
        return None