name = "mindlakesdk"

from eth_account.messages import encode_defunct
from web3 import Web3

import mindlakesdk.settings as settings
import mindlakesdk.utils
from mindlakesdk.utils import ResultType, Session, DataType
import mindlakesdk.keyhelper
from mindlakesdk.datalake import DataLake
from mindlakesdk.cryptor import Cryptor
from mindlakesdk.permission import Permission
import mindlakesdk.message

import logging

class MindLake(ResultType):

    DataType = DataType

    def __init__(self, walletPrivateKey: str, appKey: str, gateway: str = None):
        logging.debug(__name__)
        self.__session = mindlakesdk.utils.Session()
        session = self.__session
        self.datalake = DataLake(session)
        self.cryptor = Cryptor(session)
        self.permission = Permission(session)
        
        web3 = Web3(Web3.HTTPProvider(settings.WEB3API))
        walletAccount = web3.eth.account.from_key(walletPrivateKey)
        
        session.walletAddress = walletAccount.address
        session.appKey = appKey
        if gateway:
            session.gateway = gateway
        else:
            session.gateway = settings.GATEWAY
        logging.debug('gateway: %s'%session.gateway)
        logging.debug('walletAddress: %s'%session.walletAddress)

        result = mindlakesdk.message.getNounce(session)
        if not result:
            self.code = result.code
            self.message = result.message
            self.data = result.data
            return 
        nounce = result.data
        logging.debug('getNounce: %s'%nounce)
            
        result = MindLake.__login(session, walletAccount, nounce)
        if not result:
            self.code = result.code
            self.message = result.message
            self.data = result.data
            return 
        logging.debug('__login: %s'%result.data)
            
        session.mk, session.sk = mindlakesdk.keyhelper.prepareKeys(web3, walletAccount)
        logging.debug('getNounce: %s'%nounce)

        result = mindlakesdk.message.getAccountInfo(session)
        if not result:
            self.code = result.code
            self.message = result.message
            self.data = result.data
            return 
        
        if not session.isRegistered:
            result = MindLake.__registerAccount(session, self.permission)
            if not result:
                self.code = result.code
                self.message = result.message
                self.data = result.data
                return 
        else:
            result = mindlakesdk.message.getPKid(session)
            if not result:
                self.code = result.code
                self.message = result.message
                self.data = result.data
                return 
        self.code = 0
        self.message = "Success"
        self.data = None

    @staticmethod
    def __login(session: Session, walletAccount, nounce):
        msgToSign = encode_defunct(text=nounce)
        signature = walletAccount.sign_message(msgToSign)
        signatureHex = signature.signature.hex()
        return mindlakesdk.message.sendLogin(session, signatureHex)

    @staticmethod
    def __registerAccount(session: Session, permission: Permission):
        result = mindlakesdk.keyhelper.registerMK(session)
        if not result:
            return result
        result = mindlakesdk.keyhelper.registerPK(session)
        if not result:
            return result
        result = permission.grantToSelf()
        return result

connect = mindlakesdk.MindLake
    