from test_base import *

import test_base
#test_base.drop_all_cocoon_and_table(env.walletPrivateKey)

import logging
setLogging(logging.INFO)
setLogging(logging.DEBUG)
#setLogging(logging.NOTSET)


import env
#logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

import mindlakesdk

# def test_create_table_with_wrong_table_definition(walletPrivateKey, appKey):
#     print_test_functions()
#     #print(inspect.stack()[1][3])
#     mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
#     test_base.drop_all_cocoon_and_table(mindlake, appKey)
    
#     tableName = "test_table_with_nocolumns"
#     columns = []
#     result = mindlake.datalake.createTable(tableName, columns)
#     logging.info('createTable: %s %s %s'%(tableName, result.code, result.message))
#     assert result.code == 40008, 'can not create table with no columns !'

def test_table_create_insert_nonencrypted(walletPrivateKey, appKey):
    print_test_functions()
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, 'mindlakesdk.connect failed !'
    test_base.drop_all_cocoon_and_table(mindlake)
    
    tableName = 'test_table_nonencrypted'
    test_base.drop_test_table(mindlake, tableName)
    code1 = test_base.create_test_table_nonencrypted(mindlake, tableName)
    code2 = test_base.create_test_table_nonencrypted(mindlake, tableName)
    #print(code1, code2)
    assert code1 == 0 and code2 == 40008, 'can not create duplicated table with same name 1!'
        
def test_table_create_insert_encrypted(walletPrivateKey, appKey):
    print_test_functions()
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, 'mindlakesdk.connect failed !'
    test_base.drop_all_cocoon_and_table(mindlake)
    
    tableName = 'test_table_encrypted'
    test_base.drop_test_table(mindlake, tableName)
    code1 = test_base.create_test_table_encrypted(mindlake, tableName)
    code2 = test_base.create_test_table_encrypted(mindlake, tableName)
    assert code1 == 0 and code2 == 40008, 'can not create duplicated table with same name 2!'
    
def test_cocoon_create_tablelink(walletPrivateKey, appKey):
    print_test_functions()
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, 'mindlakesdk.connect failed !'
    test_base.drop_all_cocoon_and_table(mindlake)
    
    cocoonName1 = 'test_cocoon_1'
    test_base.create_test_cocoon(mindlake, cocoonName1)
    cocoonName2 = 'test_cocoon_2'
    test_base.create_test_cocoon(mindlake, cocoonName2) 
    
    result = mindlake.datalake.listCocoon()
    logging.info('listCocoon: %s %s'%(result.code, result.message))
    logging.debug(result.data)
    assert check_coocoon_exists(result.data, cocoonName1) and check_coocoon_exists(result.data, cocoonName2), 'failed to create cocoon !' 
    
    tableName1 = 'test_table_nonencrypted' 
    test_base.create_test_table_nonencrypted(mindlake, tableName1)
    test_base.link_table_to_cocoon_test(mindlake, tableName1, cocoonName1)
    tableName2 = 'test_table_encrypted'
    test_base.create_test_table_encrypted(mindlake, tableName2)
    test_base.link_table_to_cocoon_test(mindlake, tableName2, cocoonName1)
    
    result = mindlake.datalake.listTablesByCocoon(cocoonName1)
    logging.info('listTablesByCocoon: %s %s %s'%(cocoonName1, result.code, result.message))
    tables = result.data
    logging.debug(tables)
    assert check_table_exists(tables, tableName1) and check_table_exists(tables, tableName2), 'failed to link table to cocoon1 !' 
    
    test_base.link_table_to_cocoon_test(mindlake, tableName2, cocoonName2)
    
    result = mindlake.datalake.listTablesByCocoon(cocoonName2)
    logging.info('listTablesByCocoon: %s %s %s'%(cocoonName2, result.code, result.message))
    tables = result.data
    logging.debug(tables)
    assert not check_table_exists(tables, tableName1) and check_table_exists(tables, tableName2), 'failed to link table2 to cocoon2 !'  
    
    
def cases(walletPrivateKey, appKey):
    logging.info("==== start test | %s ===="%(__file__))
    # test_create_table_with_wrong_table_definition(walletPrivateKey, appKey)
    test_table_create_insert_nonencrypted(walletPrivateKey, appKey)
    test_table_create_insert_encrypted(walletPrivateKey, appKey)
    test_cocoon_create_tablelink(walletPrivateKey, appKey)
    logging.info("==== complete test | %s ===="%(__file__))
    return False

if __name__ == "__main__":
    cases(env.walletPrivateKey, env.appKey)