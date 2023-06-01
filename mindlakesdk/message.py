from mindlakesdk.utils import ResultType, request, Session
import logging

def getNounce(session: Session):
    data = {"bizType":203}
    result = request(data, session)
    if result:
        return ResultType(result["code"], result["message"], result["data"])
    else:
        return ResultType(60001, "Network error", None)


def sendLogin(session: Session, signatureHex):
    data = {"bizType":201,"walletAddress":session.walletAddress,"signature":signatureHex}
    result = request(data, session)
    if result:
        if result["code"] == 0:
            # TODO: add exception handling
            session.isLogin = True
            session.token = result["data"]["token"]
        return ResultType(result["code"], result["message"], result["data"])
    else:
        return ResultType(60001, "Network error", None)
    
def getAccountInfo(session: Session):
    data = {"bizType":120}
    result = __requestCommon(session, data)
    if result:
        session.isRegistered = result.data["isRegistered"] and result.data["isMekProvision"] and result.data["isSelfBcl"]
        session.accountID = int(result.data["mekId"])
        session.nodePK = result.data["publicKey"]
    return result
    
def getPKid(session: Session):
    data = {"bizType":103,"mekId":session.accountID}
    result = __requestCommon(session, data)
    if result:
        session.pkID = result.data
    return result
    
def sendMKRegister(session: Session, envelope):
    data = {"bizType":102, "envelope":envelope, "databasePublicKey":session.nodePK}
    return __requestCommon(session, data)
    
def sendPKRegister(session: Session, pkIDStr, publicKey, rsaSigStr, mkSigStr):
    data = {
        "bizType":104, 
        "mekId":session.accountID, 
        "pukId":pkIDStr,
        "publicKey":publicKey,
        "privateSig":rsaSigStr,
        "mekSig":mkSigStr
    }
    return __requestCommon(session, data)

def getDKbyName(session: Session, walletAddress: str = None, 
                table: str = None, column: str = None) -> ResultType:
    data = {"bizType":108, "walletAddress":walletAddress, "table":table, "column":column}
    return __requestCommon(session, data)

def getNextDKid(session: Session) -> ResultType:
    data = {"bizType":109, "mekId":session.accountID}
    return __requestCommon(session, data)

def getDKbyCid(session: Session, cid: int) -> ResultType:
    data = {"bizType":111, "ctxId":cid}
    return __requestCommon(session, data)

def sendDKRegister(session: Session, table, column, dkID, dkCipherStr, grpIDStr, gAuthStr) -> ResultType:
    data = {
        "bizType":110, 
        "mekId":session.accountID, 
        "table":table,
        "column":column,
        "dekId":dkID,
        "dekCipherStr":dkCipherStr,
        "grpIdStr":grpIDStr,
        "groupAuthStr":gAuthStr
    }
    return __requestCommon(session, data)

def getDataTypeByName(session: Session, tableName: str, columnName: str) -> ResultType:
    data = {"bizType":107, "tableName":tableName, "column":columnName}
    return __requestCommon(session, data)

def getPolicyByPKid(session: Session, issuePKid: str, subjectPKid: str) -> ResultType:
    data = {"bizType":118, "issuePukId":issuePKid, "subjectPukId":subjectPKid}
    return __requestCommon(session, data)

def getPolicyBySerialNumber(session: Session, serialNumber: str) -> ResultType:
    data = {"bizType":116, "serialNum":serialNumber}
    return __requestCommon(session, data)

def getPKidByWalletAddress(session: Session, walletAddress: str) -> ResultType:
    data = {"bizType":119, "targetWalletAddress":walletAddress}
    return __requestCommon(session, data)

def sendGrant(session: Session, policyBodyJson: str, signature: str) -> ResultType:
    data = {"bizType":115, "bclBody":policyBodyJson, "privateSig":signature}
    return __requestCommon(session, data)

def sendConfirm(session: Session, policyBodyJson: str, signature: str) -> ResultType:
    data = {"bizType":117, "bclBody":policyBodyJson, "privateSig":signature}
    return __requestCommon(session, data)

def sendSelfGrant(session: Session, policyBodyJson: str, signature: str) -> ResultType:
    data = {"bizType":106, "bclBody":policyBodyJson, "privateSig":signature}
    return __requestCommon(session, data)

def sendCreateTable(session: Session, tableName: str, columns: list, primaryKey: list = None) -> ResultType:
    data = {"bizType":123, "tableName":tableName, "columns":columns, "pkColumns":primaryKey}
    return __requestCommon(session, data)

def sendListCocoon(session: Session) -> ResultType:
    data = {"bizType":122}
    return __requestCommon(session, data)

def sendListTablesByCocoon(session: Session, cocoonName: str) -> ResultType:
    data = {"bizType":125, 'cocoonName': cocoonName}
    return __requestCommon(session, data)

def sendLinkTableToCocoon(session: Session, tableName: str, cocoonName: str) -> ResultType:
    data = {"bizType":124, 'tableName': tableName, 'cocoonName': cocoonName}
    return __requestCommon(session, data) 

def sendCreateCocoon(session: Session, cocoonName: str) -> ResultType:
    data = {"bizType":121, 'cocoonName': cocoonName}
    return __requestCommon(session, data)

def sendQuery(session: Session, executeSql) -> ResultType:
    data = {"bizType":114, 'executeSql': executeSql}
    return __requestCommon(session, data)

def sendDropCocoon(session: Session, cocoonName: str) -> ResultType:
    data = {"bizType":129, 'cocoonName': cocoonName}
    return __requestCommon(session, data)

def sendDropTable(session: Session, tableName: str) -> ResultType:
    data = {"bizType":128, 'tableName': tableName}
    return __requestCommon(session, data)

def sendListGrantee(session: Session) -> ResultType:
    data = {"bizType":126}
    return __requestCommon(session, data)

def sendListGrantedColumn(session: Session, walletAddress: str) -> ResultType:
    data = {"bizType":127, 'targetWalletAddress': walletAddress}
    return __requestCommon(session, data)

def __requestCommon(session: Session, data: str) -> ResultType:
    if session.isLogin:
        result = request(data, session)
        if result:
            return ResultType(result["code"], result["message"], result["data"])
        else:
            return ResultType(60001, "Network error", None)
    else:
        return ResultType(40001, "Not logged in", None)