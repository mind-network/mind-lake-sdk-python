import base64
import json
import struct
import uuid
from Crypto.Random import get_random_bytes
import MindLake.utils
import MindLake.message
import logging

def registerMK(session: MindLake.utils.Session):
    pubKey = session.nodePK.replace("\\n", "\n")
    ephemeralKey = get_random_bytes(16)
    sealedEphemeralKey = MindLake.utils.rsaEncrypt(pubKey, ephemeralKey)
    sealedEphemeralKeyLenBytes = len(sealedEphemeralKey).to_bytes(2, 'little')
    iv = get_random_bytes(16)
    envelope_json = __genMKEnvelope(session.mk)
    logging.debug(envelope_json)
    envelope_enc = MindLake.utils.aesEncrypt(ephemeralKey, iv, envelope_json.encode())
    big_envelope = sealedEphemeralKeyLenBytes + sealedEphemeralKey + iv + envelope_enc
    envelope = base64.b64encode(big_envelope).decode()
    return MindLake.message.sendMKRegister(session, envelope)

def __genMKEnvelope(mk, accountID = None):
    envelope = {}
    if accountID:
        envelope["mekid"] = accountID
    base64Mek = base64.b64encode(mk)
    envelope["mek"] = base64Mek.decode()
    envelope["expire"] = 0
    envelope_json = json.dumps(envelope).replace(" ", "")
    return envelope_json

def registerPK(session: MindLake.utils.Session):
    privateKey = session.sk
    publicKey = privateKey.publickey().export_key("PEM").decode()
    pkIDBytes = __genPKid(publicKey)
    pkIDStr = pkIDBytes.decode()
    session.pkID = pkIDStr
    toBeSignedBytes = bytearray(struct.pack("<q", session.accountID)) + pkIDBytes
    rsaSig = b'\x01' + MindLake.utils.rsaSign(privateKey, toBeSignedBytes)
    rsaSigStr = base64.b64encode(rsaSig).decode()
    mekSig = b'\x00' + MindLake.utils.hmacHash(session.mk, toBeSignedBytes)
    mekSigStr = base64.b64encode(mekSig).decode()
    return MindLake.message.sendPKRegister(session, pkIDStr, publicKey, rsaSigStr, mekSigStr)

def __genPKid(pubKey):
    pubKeyHash = MindLake.utils.sha256Hash(pubKey.encode("utf-8"))
    pubKeyHashBase64 = base64.b64encode(pubKeyHash)
    return pubKeyHashBase64

def encrypt_dek_b64(mek, dekid, dek):
    dekid_dek = struct.pack('<Q', dekid) + dek
    iv = get_random_bytes(16)
    encrypted_data = MindLake.utils.aesEncrypt(mek, iv, dekid_dek)
    dekCipher = b'\x03' + iv + encrypted_data
    return base64.b64encode(dekCipher).decode(encoding="ascii")

def decrypt_dek_b64(mek, dekCipherStr):
    dekCipher = base64.b64decode(dekCipherStr)
    dekid_dek = MindLake.utils.aesDecrypt(mek, dekCipher[1:17], dekCipher[17:])
    dekid = struct.unpack('<Q', dekid_dek[:8])[0]
    return dekid, dekid_dek[8:]

def genDK(session: MindLake.utils.Session, table, column):
    result = MindLake.message.getNextDKid(session)
    if not result:
        return result
    dkID = int(result.data)
    dk = get_random_bytes(16)
    dkCipherStr = encrypt_dek_b64(session.mk, dkID, dk)
    grpID = uuid.uuid4()
    grpIDbytes = grpID.bytes
    grpIDStr = str(grpID)
    gAuthStr = __digest_gAuth(session.mk, grpIDbytes, dkID)
    return MindLake.message.sendDKRegister(session, table, column, dkID, dkCipherStr, grpIDStr, gAuthStr)

def __digest_gAuth(mek, grp_id, dek_id):
    buf = grp_id + struct.pack("<q", dek_id)
    gAuth = MindLake.utils.hmacHash(mek, buf)
    return base64.b64encode(gAuth).decode(encoding="ascii")
