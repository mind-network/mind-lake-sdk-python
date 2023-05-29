name = "MindLake"

from eth_account.messages import encode_defunct
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from web3 import Web3
from base64 import b64decode, b64encode
from nacl.public import Box, PrivateKey, PublicKey

import MindLake.Settings as Settings
import MindLake.utils
from MindLake.utils import ResultType, DataType, Session
import MindLake.KeyHelper
from MindLake.DataLake import DataLake
from MindLake.Cryptor import Cryptor
from MindLake.Permission import Permission
import MindLake.message

import logging


def success(code):
    if code == 0:
        return True
    else:
        return False

__session = None

def connect(walletPrivateKey: str, appKey: str, gateWay: str = None) -> ResultType:
    global __session
    __session = MindLake.utils.Session()
    logging.debug(__name__)
    
    web3 = Web3(Web3.HTTPProvider(Settings.WEB3API))
    walletAccount = web3.eth.account.from_key(walletPrivateKey)
    DataLake.setSession(__session)
    Permission.setSession(__session)
    Cryptor.setSession(__session)
    __session.walletAddress = walletAccount.address
    __session.appKey = appKey
    logging.debug('walletAddress: %s'%__session.walletAddress)

    result = MindLake.message.getNounce(__session)
    if not result:
        return result
    nounce = result.data
    logging.debug('getNounce: %s'%nounce)
        
    result = __login(walletAccount, nounce)
    if not result:
        return result
    logging.debug('__login: %s'%result.data)
        
    __prepareKeys(web3, walletAccount)
    logging.debug('getNounce: %s'%nounce)
        
    result = MindLake.message.getAccountInfo(__session)
    if not result:
        return result
    
    if not __session.isRegistered:
        result = __registerAccount()
        if not result:
            return result
    else:
        result = MindLake.message.getPKid(__session)
        if not result:
            return result
    return ResultType(0, "Success", None)

def __login(walletAccount, nounce):
    global __session
    msgToSign = encode_defunct(text=nounce)
    signature = walletAccount.sign_message(msgToSign)
    signatureHex = signature.signature.hex()
    return MindLake.message.sendLogin(__session, signatureHex)

def __loadKeysFromChain(web3):
    contract = web3.eth.contract(address=Settings.CONTRACT_ADDRESS, abi=Settings.CONTRACT_ABI)
    return contract.functions.getKeys(__session.walletAddress).call()

def __saveKeysToChain(web3, walletAccount, MKCipher, SKCipher):
    walletAddress = __session.walletAddress
    contract = web3.eth.contract(address=Settings.CONTRACT_ADDRESS, abi=Settings.CONTRACT_ABI)
    nonce = web3.eth.get_transaction_count(walletAddress)
    gasEstimate = contract.functions.setKeys(MKCipher, SKCipher).estimate_gas({'from': walletAddress})
    txn = contract.functions.setKeys(MKCipher, SKCipher).build_transaction({
        'from': walletAddress,
        'gas': gasEstimate,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonce,
    })
    signed_txn = walletAccount.signTransaction(txn)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f'Transaction sent: {txn_hash.hex()}')

    txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    print(f'Transaction mined, status: {txn_receipt["status"]}')

def __prepareKeys(web3, walletAccount):
    mkCipher, skCipher = __loadKeysFromChain(web3)
    logging.debug('mkCipher: %s'%mkCipher)
    logging.debug('skCipher: %s'%skCipher)
    
    if mkCipher and skCipher:
        mk = __decryptWithWalletKey(walletAccount, mkCipher)
        skIV, skCipher = skCipher[:16], skCipher[16:]
        skBytes = MindLake.utils.aesDecrypt(mk, skIV, skCipher)
        sk = RSA.import_key(skBytes)
    else:
        mk = MindLake.utils.genAESKey()
        sk = MindLake.utils.genRSAKey()
        skBytes = sk.exportKey('DER')
        skIV = MindLake.utils.get_random_bytes(16)
        skCipher = MindLake.utils.aesEncrypt(mk, skIV, skBytes)
        skCipher = skIV + skCipher
        mkCipher = __encryptWithWalletKey(walletAccount, mk)
        __saveKeysToChain(web3, walletAccount, mkCipher, skCipher)
    __session.mk = mk
    __session.sk = sk
    logging.debug('mk: %s'%mk)
    logging.debug('sk: %s'%sk)

def __encryptWithWalletKey(walletAccount, msg):
    ephemeralPrivKey = PrivateKey.generate()
    privKey = PrivateKey(walletAccount.key)
    pubKey = privKey.public_key
    encryptBox = Box(ephemeralPrivKey, pubKey)
    nounce = get_random_bytes(24)
    msg = b64encode(msg)
    encryptedMsg = encryptBox.encrypt(msg, nounce)
    return bytes(ephemeralPrivKey.public_key) + nounce + encryptedMsg.ciphertext

def __decryptWithWalletKey(walletAccount, data):
    privKey = PrivateKey(walletAccount.key)
    ephemeralPubKey, nounce, ciphertext = data[:32], data[32:56], data[56:]
    box = Box(privKey, PublicKey(ephemeralPubKey))
    return b64decode(box.decrypt(ciphertext, nounce))

def __registerAccount():
    result = MindLake.KeyHelper.registerMK(__session)
    if not result:
        return result
    result = MindLake.KeyHelper.registerPK(__session)
    if not result:
        return result
    result = Permission.grantToSelf()
    return result

    