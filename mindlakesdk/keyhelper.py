import base64
import json
import logging
import struct
import uuid
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from web3 import Web3
from mindlakesdk import settings
import mindlakesdk.utils
import mindlakesdk.message
from base64 import b64decode, b64encode
from nacl.public import Box, PrivateKey, PublicKey

def registerMK(session: mindlakesdk.utils.Session):
    pubKey = session.nodePK.replace("\\n", "\n")
    ephemeralKey = get_random_bytes(16)
    sealedEphemeralKey = mindlakesdk.utils.rsaEncrypt(pubKey, ephemeralKey)
    sealedEphemeralKeyLenBytes = len(sealedEphemeralKey).to_bytes(2, 'little')
    iv = get_random_bytes(16)
    envelope_json = __genMKEnvelope(session.mk)
    envelope_enc = mindlakesdk.utils.aesEncrypt(ephemeralKey, iv, envelope_json.encode())
    big_envelope = sealedEphemeralKeyLenBytes + sealedEphemeralKey + iv + envelope_enc
    envelope = base64.b64encode(big_envelope).decode()
    return mindlakesdk.message.sendMKRegister(session, envelope)

def __genMKEnvelope(mk, accountID = None):
    envelope = {}
    if accountID:
        envelope["mekid"] = accountID
    base64MK = base64.b64encode(mk)
    envelope["mek"] = base64MK.decode()
    envelope["expire"] = 0
    envelope_json = json.dumps(envelope).replace(" ", "")
    return envelope_json

def registerPK(session: mindlakesdk.utils.Session):
    privateKey = session.sk
    publicKey = privateKey.publickey().export_key("PEM").decode()
    pkIDBytes = __genPKid(publicKey)
    pkIDStr = pkIDBytes.decode()
    session.pkID = pkIDStr
    toBeSignedBytes = bytearray(struct.pack("<q", session.accountID)) + pkIDBytes
    rsaSig = b'\x01' + mindlakesdk.utils.rsaSign(privateKey, toBeSignedBytes)
    rsaSigStr = base64.b64encode(rsaSig).decode()
    mkSig = b'\x00' + mindlakesdk.utils.hmacHash(session.mk, toBeSignedBytes)
    mkSigStr = base64.b64encode(mkSig).decode()
    return mindlakesdk.message.sendPKRegister(session, pkIDStr, publicKey, rsaSigStr, mkSigStr)

def __genPKid(pubKey):
    pubKeyHash = mindlakesdk.utils.sha256Hash(pubKey.encode("utf-8"))
    pubKeyHashBase64 = base64.b64encode(pubKeyHash)
    return pubKeyHashBase64

def encryptDKb64(mk, dkID, dk):
    dkID_dk = struct.pack('<Q', dkID) + dk
    iv = get_random_bytes(16)
    encrypted_data = mindlakesdk.utils.aesEncrypt(mk, iv, dkID_dk)
    dkCipher = b'\x03' + iv + encrypted_data
    return base64.b64encode(dkCipher).decode(encoding="ascii")

def decryptDKb64(mk, dkCipherStr):
    dkCipher = base64.b64decode(dkCipherStr)
    dkID_dk = mindlakesdk.utils.aesDecrypt(mk, dkCipher[1:17], dkCipher[17:])
    dkID = struct.unpack('<Q', dkID_dk[:8])[0]
    return dkID, dkID_dk[8:]

def genDK(session: mindlakesdk.utils.Session, table, column):
    result = mindlakesdk.message.getNextDKid(session)
    if not result:
        return result
    dkID = int(result.data)
    dk = get_random_bytes(16)
    dkCipherStr = encryptDKb64(session.mk, dkID, dk)
    grpID = uuid.uuid4()
    grpIDbytes = grpID.bytes
    grpIDStr = str(grpID)
    gAuthStr = __digest_gAuth(session.mk, grpIDbytes, dkID)
    return mindlakesdk.message.sendDKRegister(session, table, column, dkID, dkCipherStr, grpIDStr, gAuthStr)

def __digest_gAuth(mk, grpID, dkID):
    buf = grpID + struct.pack("<q", dkID)
    gAuth = mindlakesdk.utils.hmacHash(mk, buf)
    return base64.b64encode(gAuth).decode(encoding="ascii")

def prepareKeys(web3, walletAccount):
    mkCipher, skCipher = __loadKeysFromChain(walletAccount.address, web3)
    logging.debug('mkCipher: %s'%mkCipher)
    logging.debug('skCipher: %s'%skCipher)
    
    if mkCipher and skCipher:
        mk = __decryptWithWalletKey(walletAccount, mkCipher)
        skIV, skCipher = skCipher[:16], skCipher[16:]
        skBytes = mindlakesdk.utils.aesDecrypt(mk, skIV, skCipher)
        sk = RSA.import_key(skBytes)
    else:
        mk = mindlakesdk.utils.genAESKey()
        sk = mindlakesdk.utils.genRSAKey()
        skBytes = sk.exportKey('DER', pkcs=8)
        skIV = mindlakesdk.utils.get_random_bytes(16)
        skCipher = mindlakesdk.utils.aesEncrypt(mk, skIV, skBytes)
        skCipher = skIV + skCipher
        mkCipher = __encryptWithWalletKey(walletAccount, mk)
        __saveKeysToChain(web3, walletAccount, mkCipher, skCipher)
    logging.debug('mk: %s'%mk)
    logging.debug('sk: %s'%sk)
    return mk, sk

def __saveKeysToChain(web3, walletAccount, MKCipher, SKCipher):
    walletAddress = walletAccount.address
    contract = web3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)
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

def __loadKeysFromChain(walletAddress: str, web3: Web3):
    contract = web3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=settings.CONTRACT_ABI)
    return contract.functions.getKeys(walletAddress).call()

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