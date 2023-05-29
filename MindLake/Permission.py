import base64
import datetime
import json
import logging
import uuid

from MindLake.utils import ResultType, Session
import MindLake.utils
import MindLake.message

class Permission:
    __session = None

    def setSession(session: Session):
        Permission.__session = session

    def grant(targetWalletAddress: str, columns: list) -> ResultType:
        session = Permission.__session
        result = MindLake.message.getPKidByWalletAddress(session, targetWalletAddress)
        if not result:
            return result
        targetPKID = result.data["publicKeyId"]
        policy = {
            'issuer_dek_group': [],
            'subject_dek_group': []
        }
        for column in columns:
            tableName, columnName = column.split('.')
            result = MindLake.message.getDKbyName(session, session.walletAddress, tableName, columnName)
            if not result:
                return result
            groupID = result.data['groupId']
            policy['issuer_dek_group'].append({
                'groupid': groupID,
                'min': 1,
                'max': 1000
            })
        result = Permission.__createPolicyBody(Permission.__session.pkID, targetPKID, policy)
        if not result:
            return result
        policyBodyJson = result.data
        signature = Permission.__signPolicy(policyBodyJson)
        signatureB64 = base64.b64encode(signature).decode('utf-8')
        return MindLake.message.sendGrant(Permission.__session, policyBodyJson, signatureB64)

    def confirm(policyID: str) -> ResultType:
        result = MindLake.message.getPolicyBySerialNumber(Permission.__session, policyID)
        if not result:
            return result
        policyBodyJson = result.data
        policyBody = json.loads(policyBodyJson)
        if policyBody['subject_pukid'] != Permission.__session.pkID:
            return MindLake.utils.ResultType(60002, "The policy is not for you")
        signature = Permission.__signPolicy(policyBodyJson)
        signatureB64 = base64.b64encode(signature).decode('utf-8')
        return MindLake.message.sendConfirm(Permission.__session, policyBodyJson, signatureB64)
    
    def revoke(targetWalletAddress: str):
        return Permission.grant(targetWalletAddress, [])

    def grantToSelf():
        result = MindLake.message.getDKbyName(Permission.__session)
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
        result = Permission.__createPolicyBody(Permission.__session.pkID,
                                Permission.__session.pkID,
                                policy)
        if not result:
            return result
        policyBodyJson = result.data
        signature = Permission.__signPolicy(policyBodyJson)
        signatureB64 = base64.b64encode(signature).decode('utf-8')
        return MindLake.message.sendSelfGrant(Permission.__session, policyBodyJson, signatureB64)

    def __createPolicyBody(issuerPukid, 
                            subjectPukid,
                            policy,
                            version = 1,
                            serialNum = None,
                            notBefore = None,
                            notAfter = None,
                            resultDek = "SUBJECT",
                            operation = ['*'],
                            postProc = "NULL",
                            preProc = "NULL") -> ResultType:
        result = MindLake.message.getPolicyByPKid(Permission.__session, issuerPukid, subjectPukid)
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
        policyBody['policies']['result_dek'] = resultDek
        policyBody['policies'].update(policy)
        policyBodyJson = json.dumps(policyBody)
        return ResultType(0, "Success", policyBodyJson)
    
    def __signPolicy(policyBodyJson) -> bytes:
        toBeSignedBytes = policyBodyJson.encode('utf-8')
        signature = MindLake.utils.rsaSign(Permission.__session.sk, toBeSignedBytes)
        return b'\x01' + signature
    
    def listGrantee() -> ResultType:
        return MindLake.message.sendListGrantee(Permission.__session)  
    
    def listGrantedColumn(walletAddress: str) -> ResultType:
        return MindLake.message.sendListGrantedColumn(Permission.__session, walletAddress) 
    