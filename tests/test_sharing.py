from test_base import *

import datetime
import pprint
import test_base
# test_base.drop_all_cocoon_and_table(env.walletPrivateKey)
import mindlakesdk

import logging
setLogging(logging.INFO)
# setLogging(logging.DEBUG)

import env
#logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

print("============= start test ============")

def prepare_test(mindlake: MindLake):
    tableName = 'test_table_encrypted_1'
    test_base.drop_test_table(mindlake, tableName)
    test_base.create_test_table_encrypted(mindlake, tableName)

# by now, I should have at least one table and one cocoon, and table link to cocoon
print("============= test preparation completed ============")

def test_insert_encrypted_data(mindlake: MindLake, data):
    tableName = 'test_table_encrypted_1'
    encryptedData = {}
    for k, v in data.items():
        print(f"===== encrypt {k} in column =====")
        currentColumn = 'data' + k
        q = mindlake.cryptor.encrypt(v, f'{tableName}.{currentColumn}')
        print('Code: ', q.code, q.message, f'encrypt {k}')
        assert q and isinstance(q.data, str) and q.data[:2] == '\\x', 'encryption test failed !'
        encryptedData[currentColumn] = q.data

    sql = f"""INSERT INTO "{tableName}" 
    VALUES (
        '{encryptedData['dataint4']}',
        '{encryptedData['dataint8']}',
        '{encryptedData['datafloat4']}',
        '{encryptedData['datafloat8']}',
        '{encryptedData['datadecimal']}',
        '{encryptedData['datatext']}',
        '{encryptedData['datatimestamp']}') RETURNING *"""
    print(sql)
    q = mindlake.datalake.query(sql)
    print('Code: ', q.code, q.message, 'INSERT')
    assert q, 'encryption test failed !'
    # logging.debug(q.data)

def test_query_decrypt_shared(mindlake: MindLake, ownerWalletAddress, data, grantColumn):
    tableName = 'test_table_encrypted_1'

    print("===== select * =====")
    queryResult = mindlake.datalake.query(f'SELECT * FROM "{ownerWalletAddress[2:].lower()}"."{tableName}"')
    print('Code: ', queryResult.code, queryResult.message, 'SELECT')
    # logging.debug(queryResult.data)
    count_select_all = len(queryResult.data['data'])
    assert queryResult and count_select_all == 1, 'decryption test failed !'
    row = queryResult.data['data'][0]
    columnList = queryResult.data['columnList']
    for i, cell in enumerate(row):
        print(f"===== decrypt column num {i} {columnList[i]}=====")
        q = mindlake.cryptor.decrypt(cell)
        print('Code: ', q.code, q.message, 'DECRYPT ', columnList[i])
        print('Decrypted: Column', i, columnList[i], q.data)
        print('Origin:', data[columnList[i][4:]])
        if columnList[i] == 'datafloat4' or columnList[i] == 'datafloat8':
            if columnList[i][4:] in grantColumn:
                assert q and abs(q.data - data[columnList[i][4:]]) < 0.01, 'decryption test failed !'
            else:
                assert q.code == 60003, 'decryption test failed !'
        else:
            if columnList[i][4:] in grantColumn:
                assert q and q.data == data[columnList[i][4:]], 'decryption test failed !'
            else:
                assert q.code == 60003, 'decryption test failed !'

def test_share_column(mindlake: MindLake, granteeWalletAddress, grantColumn):
    tableName = 'test_table_encrypted_1'
    print(f"===== share column {' '.join(grantColumn)} =====")
    q = mindlake.permission.grant(granteeWalletAddress, [tableName + '.data' + column for column in grantColumn])
    print('Code: ', q.code, q.message, 'SHARE COLUMN')
    print('serialNum: ', q.data)
    assert q, 'share column failed !'
    return q.data

def test_confirm_share(mindlake: MindLake, serialNum):
    print(f"===== confirm share {serialNum} =====")
    q = mindlake.permission.confirm(serialNum)
    print('Code: ', q.code, q.message, 'CONFIRM SHARE')
    assert q, 'confirm share failed !'

def test_revoke_share(mindlake: MindLake, granteeWalletAddress):
    print(f"===== revoke share =====")
    q = mindlake.permission.revoke(granteeWalletAddress)
    print('Code: ', q.code, q.message, 'REVOKE SHARE')
    assert q.code == 0, 'revoke share failed !'
    
    
def test_share_to_nobody(mindlake:MindLake, grantColumn):
    tableName = 'test_table_encrypted_1'
    print(f"===== share column {' '.join(grantColumn)} =====")
    q = mindlake.permission.grant(env.walletAddressNobody, [tableName + '.data' + column for column in grantColumn])
    print('Code: ', q.code, q.message, 'SHARE COLUMN')
    print('serialNum: ', q.data)
    assert q.code == 0, 'can not share to nobody !'
    return q.data


def test_list_guarantee():
    pass
    
def cases(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey):
    mindlakeAlice = mindlakesdk.connect(walletPrivateKeyAlice, appKey, env.GATEWAY)
    assert mindlakeAlice, 'connect failed !'
    test_base.drop_all_cocoon_and_table(mindlakeAlice)
    prepare_test(mindlakeAlice)
    data = {
        'int4': 123,
        'int8': 1234567890,
        'float4': 1.2345678901234567890,
        'float8': 1.2345678901234567890,
        'decimal': 12345678901234567890,
        'text': 'Hello',
        'timestamp': datetime.datetime.now()
    }
    test_insert_encrypted_data(mindlakeAlice, data)
    r = mindlakeAlice.permission.revoke(walletAddressBob)
    assert r, r.message
    print("No permission granted. Attemp to decrypt all columns")
    mindlakeBob = mindlakesdk.connect(walletPrivateKeyBob, appKey, env.GATEWAY)
    assert mindlakeBob, mindlakeBob.message
    test_query_decrypt_shared(mindlakeBob, walletAddressAlice, data, [])
    print("============= complete 1 ============")

    grantColumn = ['int4']
    serialNum = test_share_column(mindlakeAlice, walletAddressBob, grantColumn)
    test_confirm_share(mindlakeBob, serialNum)
    print(f"Permission of {' '.join(grantColumn)} granted. Attemp to decrypt all columns")
    test_query_decrypt_shared(mindlakeBob, walletAddressAlice, data, grantColumn)
    print("============= complete 2 ============")

    grantColumn = ['int8', 'float4', 'float8']
    serialNum = test_share_column(mindlakeAlice, walletAddressBob, grantColumn)
    print(f"Permission of {' '.join(grantColumn)} granted. Attemp to decrypt all columns")
    test_confirm_share(mindlakeBob, serialNum)
    test_query_decrypt_shared(mindlakeBob, walletAddressAlice, data, grantColumn)
    print("============= complete 3 ============")

    test_revoke_share(mindlakeAlice, walletAddressBob)
    print(f"Revoke all permission. Attemp to decrypt all columns")
    test_query_decrypt_shared(mindlakeBob, walletAddressAlice, data, [])
    print("============= complete 4 ============")

if __name__ == "__main__":
    cases(env.walletPrivateKeyAlice, env.walletPrivateKeyBob, env.walletAddressAlice, env.walletAddressBob, env.appKey)