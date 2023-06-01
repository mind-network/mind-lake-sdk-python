from test_base import *

import test_base
# test_base.drop_all_cocoon_and_table(env.walletPrivateKey)

import logging
setLogging(logging.INFO)
# setLogging(logging.DEBUG)

import env
# logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

import mindlakesdk
print("============= start test ============")

def prepare_test(mindlake: MindLake):
    tableName = 'test_table_encryption'
    test_base.drop_test_table(mindlake, tableName)
    test_base.create_test_table_encrypted(mindlake, tableName)

# by now, I should have at least one table and one cocoon, and table link to cocoon
print("============= test preparation completed ============")


def test_insert_encrypted_data(mindlake: MindLake, data):
    print_test_functions()
    tableName = 'test_table_encryption'
    q = test_base.insert_test_table_encrypted(mindlake, tableName, data)
    assert q.code == 0, 'encryption test failed !'
    logging.debug(q.data)

def test_query_decrypt(mindlake: MindLake, data):
    print_test_functions()
    tableName = 'test_table_encryption'

    print("===== select * =====")
    queryResult = mindlake.datalake.query(f'SELECT * FROM "{tableName}"')
    print('Code: ', queryResult.code, queryResult.message, 'SELECT')
    logging.debug(queryResult.data)
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
            assert q and abs(q.data - data[columnList[i][4:]]) < 0.01, 'decryption test failed !'
        else:
            assert q and q.data == data[columnList[i][4:]], 'decryption test failed !'

def test_constant_encrypt_decrypt(mindlake: MindLake, data):
    print_test_functions()
    encryptedData = {}
    for k, v in data.items():
        print(f"===== encrypt constant {k} =====")
        q = mindlake.cryptor.encrypt(v, mindlake.DataType[k])
        print('Code: ', q.code, q.message, f'encrypt {k}')
        assert q and isinstance(q.data, str) and q.data[:2] == '\\x', 'encryption test failed !'
        encryptedData[k] = q.data
    
    logging.debug(encryptedData)

    for k, v in encryptedData.items():
        print(f"===== decrypt contant {k} =====")
        q = mindlake.cryptor.decrypt(v)
        print('Code: ', q.code, q.message, f'decrypt {k}')
        print(k, q.data)
        if k == mindlake.DataType.float4.name or k == mindlake.DataType.float8.name:
            assert q and abs(q.data - data[k]) < 0.01, 'decryption test failed !'
        else:
            assert q and q.data == data[k], 'decryption test failed !'

def cases(walletPrivateKey, appKey):
    data =  {
        'int4': 123,
        'int8': 1234567890,
        'float4': 1.2345678901234567890,
        'float8': 1.2345678901234567890,
        'decimal': 12345678901234567890,
        'text': 'Hello',
        'timestamp': datetime.datetime.now()
    }
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, mindlake.message
    test_base.drop_all_cocoon_and_table(mindlake)
    prepare_test(mindlake)
    test_insert_encrypted_data(mindlake, data)
    test_query_decrypt(mindlake, data)
    test_constant_encrypt_decrypt(mindlake, data)
    print("============= complete 1 ============")

if __name__ == "__main__":
    cases(env.walletPrivateKeyBob, env.appKey)
