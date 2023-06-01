import datetime
from decimal import Decimal
import struct
from enum import Enum
from Crypto.Random import get_random_bytes
from mindlakesdk.utils import ResultType, Session, DataType
import mindlakesdk.message
import mindlakesdk.keyhelper
import mindlakesdk.utils

class Cryptor:

    class EncType(Enum):
        enc_int4 = 1
        enc_int8 = 2
        enc_float4 = 3
        enc_float8 = 4
        enc_decimal = 6
        enc_text = 7
        enc_timestamp = 8

    def __init__(self, session: Session):
        self.__session = session
    
    def encrypt(self, data, columnOrType: str|DataType) -> ResultType:
        if isinstance(columnOrType, DataType):
            dataType = columnOrType
            result = mindlakesdk.message.getDKbyName(self.__session)
            if not result:
                return result
        else:
            tableName, columnName = columnOrType.split('.')
            result = mindlakesdk.message.getDataTypeByName(self.__session, tableName, columnName)
            if not result:
                return result
            dataType = DataType(result.data)
            result = mindlakesdk.message.getDKbyName(self.__session, self.__session.walletAddress, tableName, columnName)
            # Temporary solution for MS not returning Error Code
            if result.code == 40010:
                # DK not found, create one
                result = mindlakesdk.keyhelper.genDK(self.__session, tableName, columnName)
                if not result:
                    return result
            elif not result:
                return result
            else:
                pass
        encTypeNum = Cryptor.EncType['enc_' + dataType.name].value
        data = Cryptor.__encodeByDataType(data, dataType)
        ctxid = result.data['ctxId']
        dkCipher = result.data['encryptedDek']
        dkID, dk = mindlakesdk.keyhelper.decryptDKb64(self.__session.mk, dkCipher)
        alg = result.data['algorithm']
        header = Cryptor.__genCryptoHeader(ctxid, encTypeNum)
        checkCode = Cryptor.__genCheckCode(data, 1)
        data_to_enc = data + checkCode
        if alg == 3:
            iv = get_random_bytes(16)
            encrypted_data = mindlakesdk.utils.aesEncrypt(dk, iv, data_to_enc)
        elif alg == 0:
            iv = get_random_bytes(12)
            encrypted_data = mindlakesdk.utils.aesGCMEncrypt(dk, iv, data_to_enc)
        buf = header + iv + encrypted_data
        tmp = buf[1:]
        checkCode2 = Cryptor.__genCheckCode(tmp, 1)
        result = checkCode2 + tmp
        resultHex = '\\x' + result.hex()
        return ResultType(0, None, resultHex)

    def __encodeByDataType(data, dataType: DataType) -> bytes:
        if dataType == DataType.int4:
            result = struct.pack("<i", data)
        elif dataType == DataType.int8:
            result = struct.pack("<q", data)
        elif dataType == DataType.float4:
            result = struct.pack("<f", data)
        elif dataType == DataType.float8:
            result = struct.pack("<d", data)
        elif dataType == DataType.decimal:
            val = Decimal(data)
            val_str = str(val)
            result = val_str.encode('utf-8')
        elif dataType == DataType.text:
            result = data.encode('utf-8')
        elif dataType == DataType.timestamp:
            u_sec = int(data.timestamp() * 1000000)
            u_sec -= 946684800000000
            u_sec += int(datetime.datetime.now().astimezone().utcoffset().total_seconds() * 1000000)
            result = struct.pack('<q', u_sec)
        else:
            raise Exception("Unsupported encryption type")
        return result

    def decrypt(self, cipher: bytes|str) -> ResultType:
        if isinstance(cipher, str):
            data = bytes.fromhex(cipher[2:])
        else:
            data = cipher
        header = Cryptor.__extractCryptoHeader(data)
        encTypeNum = Cryptor.__extractEncType(header)
        ctxId = Cryptor.__extractCtxId(header)
        result = mindlakesdk.message.getDKbyCid(self.__session, ctxId)
        if not result:
            return result
        dkCipher = result.data['encryptedDek']
        # TODO: catch decryption error
        try:
            dkID, dk = mindlakesdk.keyhelper.decryptDKb64(self.__session.mk, dkCipher)
        except:
            return ResultType(60003, "Can't handle DK")
        alg = result.data['algorithm']
        if alg is None:
            raise Exception("Cannot find data key by ctxId")
        else:
            idx = (header[1] & 0x7) + 2
            if alg == 3:
                iv = data[idx:idx+16]
                cipherBlob = data[idx+16:]
                plainBlob = mindlakesdk.utils.aesDecrypt(dk, iv, cipherBlob)
            elif alg == 0:
                iv = data[idx:idx+12]
                idx += 12
                mac = data[idx:idx+16]
                idx += 16
                cipherBlob = data[idx:]
                plainBlob = mindlakesdk.utils.aesGCMDecrypt(dk, iv, cipherBlob, mac)
            else:
                raise Exception("Unsupported algorithm to decrypt")
            result = plainBlob[:-1]
            checkCode = plainBlob[-1:]
            checkCode2 = Cryptor.__genCheckCode(result, 1)
            if checkCode != checkCode2:
                raise Exception("Check code is not correct")
            result = Cryptor.__decodeByEncType(result, Cryptor.EncType(encTypeNum))
            return ResultType(0, None, result)

    def __decodeByEncType(data, encType: EncType):
        if encType == Cryptor.EncType.enc_int4:
            size = struct.calcsize('<i')
            buf = data[:size]
            result = struct.unpack('<i', buf)[0]
        elif encType == Cryptor.EncType.enc_int8:
            size = struct.calcsize('<q')
            buf = data[:size]
            result = struct.unpack('<q', buf)[0]
        elif encType == Cryptor.EncType.enc_float4:
            size = struct.calcsize('<f')
            buf = data[:size]
            result = struct.unpack('<f', buf)[0]
        elif encType == Cryptor.EncType.enc_float8:
            size = struct.calcsize('<d')
            buf = data[:size]
            result = struct.unpack('<d', buf)[0]
        elif encType == Cryptor.EncType.enc_decimal:
            result = Decimal(data.decode('utf-8'))
        elif encType == Cryptor.EncType.enc_text:
            result = data.decode('utf-8')
        elif encType == Cryptor.EncType.enc_timestamp:
            size = struct.calcsize('<q')
            buf = data[:size]
            u_sec = struct.unpack('<q', buf)[0]
            u_sec += 946684800000000
            u_sec -= int(datetime.datetime.now().astimezone().utcoffset().total_seconds() * 1000000)
            time_stamp = u_sec / 1000000.0
            result = datetime.datetime.fromtimestamp(time_stamp)
        else:
            raise Exception("Unsupported encryption type")
        return result

    def __extractCryptoHeader(data):
        header = bytearray()
        index = 0
        for i in range(1):
            header.append(data[index])
            index += 1
        assert index == 1
        header.append(data[index])
        index += 1
        rng = header[1] & 0x7
        for i in range(rng):
            header.append(data[index])
            index += 1
        return header
    
    def __extractEncType(header):
        tmp_value = header[1]
        type_value = (tmp_value & 0xF8) >> 3
        return type_value
    
    def __extractCtxId(header):
        ctxIdLen = header[1] & 0x7
        assert len(header) == ctxIdLen + 2
        ctxId = 0
        for i in range(ctxIdLen):
            index = len(header) - 1 - i
            ctxId = ctxId << 8 | (header[index] & 0xFF)
        return ctxId

    def __genCryptoHeader(ctxid, encType):
        head = bytearray(bytes.fromhex('0000'))

        tmp_value = head[1]
        tmp_value = tmp_value & 0xFFFFFF07
        tmp_value = tmp_value | (encType << 3)
        head[1] = tmp_value

        tmp = ctxid
        while tmp != 0:
            head.append(tmp & 0xFF)
            tmp >>= 8

        ctxLen = len(head) - 2

        tmp_val = head[1]
        tmp_val = (tmp_val & 0xFFFFFFF8) | (ctxLen & 0x7)
        head[1] = tmp_val
        return bytes(head)

    def __genCheckCode(data, resultSize):
        tmpCode = bytearray(resultSize)
        for i in range(len(data)):
            n = i % resultSize
            tmpCode[n] ^= data[i]
        return bytes(tmpCode)
    