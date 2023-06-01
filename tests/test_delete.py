from test_base import *

import test_base

import logging
setLogging(logging.INFO)
# setLogging(logging.DEBUG)

import env
# logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

import mindlakesdk
print("============= start test ============")



def test_delete_nonencrypted(mindlake: MindLake):
    print_test_functions()    
    tableName = 'test_table_nonencrypted'
    test_base.drop_test_table(mindlake, tableName)
    test_base.create_test_table_nonencrypted(mindlake, tableName)
    count_select_all = test_base.insert_test_table_nonencrypted(mindlake, tableName)
    assert count_select_all == 2, "nonencrypted table insert wrong !"
    
    sql = "DELETE FROM %s WHERE mid = '%s'"%(tableName, 'a1')
    print(sql)
    q = mindlake.datalake.query(sql)
    print('Code: ', q.code, q.message, 'INSERT')
    logging.debug(q.data)
    assert q.code == 0, 'delete can not work'
    
    q = mindlake.datalake.query(f"SELECT * FROM {tableName}")
    print('Code: ', q.code, q.message, 'SELECT')
    logging.debug(q.data)
    count_select_all = len(q.data['data'])
    assert count_select_all == 0, 'delete does not work in nonencrypted table !' 
    
def test_delete_encrypted(mindlake: MindLake):
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
    test_base.insert_test_table_encrypted(mindlake, tableName, data)
    
    queryResult = mindlake.datalake.query(f"SELECT * FROM {tableName}")
    print('Code: ', queryResult.code, queryResult.message, 'SELECT')
    logging.debug(queryResult.data)
    count_select_all = len(queryResult.data['data'])
    assert queryResult.code == 0 and count_select_all == 2, 'decryption test failed !'
    
    q = mindlake.cryptor.encrypt(123, mindlake.DataType.int4)
    sql = f"""DELETE FROM "{tableName}" WHERE dataint4 = '{q.data}'"""
    q = mindlake.datalake.query(sql)
    print('Code: ', q.code, q.message, 'DELETE')
    logging.debug(q.data)
    assert q.code == 0, 'delete does not work in encrypted table !'
    
    q = mindlake.datalake.query(f"SELECT * FROM {tableName}")
    print('Code: ', q.code, q.message, 'SELECT')
    assert q, 'select failed !'
    logging.debug(q.data)
    count_select_all = len(q.data['data'])
    assert count_select_all == 0, 'delete does not work in encrypted table !' 
    

print("============= complete test ============")    
def cases(walletPrivateKey, appKey):
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, 'mindlakesdk.connect failed !'
    test_base.drop_all_cocoon_and_table(mindlake)
    test_delete_nonencrypted(mindlake)
    test_delete_encrypted(mindlake)
    
if __name__ == "__main__":
    cases(env.walletPrivateKey, env.appKey)
