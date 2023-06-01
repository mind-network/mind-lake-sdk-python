import base64
import datetime
import json
import logging
import uuid

from mindlakesdk.utils import ResultType, Session
import mindlakesdk.utils
import mindlakesdk.message

class Permission:
    def __init__(self, session: Session):
        self.__session = session

    def grant(self, targetWalletAddress: str, columns: list) -> ResultType:
        session = self.__session
        result = mindlakesdk.message.getPKidByWalletAddress(session, targetWalletAddress)
        if not result:
            return result
        targetPKID = result.data["publicKeyId"]
        logging.debug("Get PK ID from wallet address: " + targetWalletAddress + ' - ' + targetPKID)
        policy = {
            'issuer_dek_group': [],
            'subject_dek_group': []
        }
        for column in columns:
            tableName, columnName = column.split('.')
            result = mindlakesdk.message.getDKbyName(session, session.walletAddress, tableName, columnName)
            if not result:
                return result
            groupID = result.data['groupId']
            policy['issuer_dek_group'].append({
                'groupid': groupID,
                'min': 1,
                'max': 1000
            })
        result = self.__createPolicyBody(self.__session.pkID, targetPKID, policy)
        if not result:
            return result
        policyBodyJson = result.data
        signature = self.__signPolicy(policyBodyJson)
        signatureB64 = base64.b64encode(signature).decode('utf-8')
        return mindlakesdk.message.sendGrant(self.__session, policyBodyJson, signatureB64)

    def confirm(self, policyID: str) -> ResultType:
        result = mindlakesdk.message.getPolicyBySerialNumber(self.__session, policyID)
        if not result:
            return result
        policyBodyJson = result.data
        policyBody = json.loads(policyBodyJson)
        if policyBody['subject_pukid'] != self.__session.pkID:
            logging.debug("Self pukid: " + self.__session.pkID)
            logging.debug("Policy pukid: " + policyBody['subject_pukid'])
            return mindlakesdk.utils.ResultType(60002, "The policy is not for you")
        signature = self.__signPolicy(policyBodyJson)
        signatureB64 = base64.b64encode(signature).decode('utf-8')
        return mindlakesdk.message.sendConfirm(self.__session, policyBodyJson, signatureB64)
    
    def revoke(self, targetWalletAddress: str):
        return self.grant(targetWalletAddress, [])

    def grantToSelf(self):
        result = mindlakesdk.message.getDKbyName(self.__session)
        if not result:
            return result
        groupID = result.data['groupId']
        policy = {
            'issuer_dek_group': [{
                'groupid': groupID,
                'min': 1,
                'max': 1000
            }],
            'subject_dek_group': [{
                'groupid': groupID,
                'min': 1,
                'max': 1000
            }]
        }
        result = self.__createPolicyBody(self.__session.pkID,
                                self.__session.pkID,
                                policy)
        if not result:
            return result
        policyBodyJson = result.data
        signature = self.__signPolicy(policyBodyJson)
        signatureB64 = base64.b64encode(signature).decode('utf-8')
        return mindlakesdk.message.sendSelfGrant(self.__session, policyBodyJson, signatureB64)

    def __createPolicyBody(self,
                            issuerPukid, 
                            subjectPukid,
                            policy,
                            version = 1,
                            serialNum = None,
                            notBefore = None,
                            notAfter = None,
                            resultDK = "SUBJECT",
                            operation = ['*'],
                            postProc = "NULL",
                            preProc = "NULL") -> ResultType:
        result = mindlakesdk.message.getPolicyByPKid(self.__session, issuerPukid, subjectPukid)
        if not result:
            return result
        policyBodyJson = result.data
        if policyBodyJson:
            logging.debug("Policy already exists, loading existing Policy")
            policyBody = json.loads(policyBodyJson)
        else:
            if not serialNum:
                serialNum = str(uuid.uuid4())
            if not notBefore:
                notBefore = datetime.datetime.now()
            if not notAfter:
                notAfter = datetime.datetime.now() + datetime.timedelta(days=365)
            policyBody = {}
            policyBody['version'] = version
            policyBody['serial_num'] = serialNum
            policyBody['issuer_pukid'] = issuerPukid
            policyBody['subject_pukid'] = subjectPukid
            policyBody['validity'] = {}
            policyBody['validity']['not_after'] = notAfter.astimezone().strftime('%Y%m%d%H%M%S%z')
            policyBody['validity']['not_before'] = notBefore.astimezone().strftime('%Y%m%d%H%M%S%z')
        policyBody['policies'] = {}
        policyBody['policies']['operation'] = operation
        policyBody['policies']['post_proc'] = postProc
        policyBody['policies']['pre_proc'] = preProc
        policyBody['policies']['result_dek'] = resultDK
        policyBody['policies'].update(policy)
        policyBodyJson = json.dumps(policyBody)
        return ResultType(0, "Success", policyBodyJson)
    
    def __signPolicy(self, policyBodyJson) -> bytes:
        toBeSignedBytes = policyBodyJson.encode('utf-8')
        signature = mindlakesdk.utils.rsaSign(self.__session.sk, toBeSignedBytes)
        return b'\x01' + signature
    
    def listGrantee(self) -> ResultType:
        return mindlakesdk.message.sendListGrantee(self.__session)  
    
    def listGrantedColumn(self, walletAddress: str) -> ResultType:
        return mindlakesdk.message.sendListGrantedColumn(self.__session, walletAddress) 
    