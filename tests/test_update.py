from test_base import *

import test_base

import logging
setLogging(logging.INFO)
# setLogging(logging.DEBUG)

import env
# logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

import mindlakesdk
print("============= start test ============")


def test_update_nonencrypted(mindlake: MindLake):
    print_test_functions()
    
    tableName = 'test_table_nonencrypted'
    test_base.drop_test_table(mindlake, tableName)
    test_base.create_test_table_nonencrypted(mindlake, tableName)
    count_select_all = test_base.insert_test_table_nonencrypted(mindlake, tableName)
    assert count_select_all == 2, "nonencrypted table insert wrong !"
    
    data = test_base.update_test_table_nonencrypted(mindlake, tableName)
    assert data[0][1] == 'b11', "nonencrypted table update wrong !" 
    
def test_update_encrypted(mindlake: MindLake):
    print_test_functions()
    
    tableName = 'test_table_encrypted'
    test_base.drop_test_table(mindlake, tableName)
    test_base.create_test_table_encrypted(mindlake, tableName)
    data =  {
        'int4': 123,
        'int8': 1234567890,
        'float4': 1.2345678901234567890,
        'float8': 1.2345678901234567890,
        'decimal': 12345678901234567890,
        'text': 'Hello',
        'timestamp': datetime.datetime.now()
    }
    test_base.insert_test_table_encrypted(mindlake, tableName, data)
    
    data2 =  {
        'int4': 123,
        'int8': 5234567890,
        'float4': 5.2345678901234567890,
        'float8': 5.2345678901234567890,
        'decimal': 52345678901234567890,
        'text': 'world',
        'timestamp': datetime.datetime.now()
    }
    update_test_table_encrypted(mindlake, tableName, data2, data2['int4'])
    
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
        print('Origin:', data2[columnList[i][4:]])
        if columnList[i] == 'datafloat4' or columnList[i] == 'datafloat8':
            assert q and abs(q.data - data2[columnList[i][4:]]) < 0.01, 'decryption test failed !'
        else:
            assert q and q.data == data2[columnList[i][4:]], 'decryption test failed !'


print("============= complete test ============")  
def cases(walletPrivateKey, appKey):
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, 'mindlakesdk.connect failed !'
    test_base.drop_all_cocoon_and_table(mindlake)
    test_update_nonencrypted(mindlake)
    test_update_encrypted(mindlake)
      
if __name__ == "__main__":
    cases(env.walletPrivateKey, env.appKey)
    
