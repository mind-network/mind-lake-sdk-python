from test_base import *

import test_base
import mindlakesdk


import logging
setLogging(logging.INFO)
# setLogging(logging.DEBUG)

import env
#logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

print("============= start test ============")


print("============= link encrypted table ============")    
def test_link_table_to_mywalletcocoon_alice_encrypted(mindlake: MindLake):
    print_test_functions()
    
    tableNameAlice = 'test_table_encrypted_Alice'
    test_base.drop_test_table(mindlake, tableNameAlice)
    test_base.create_test_table_encrypted(mindlake, tableNameAlice)
    data = {
        'int4': 123,
        'int8': 1234567890,
        'float4': 1.2345678901234567890,
        'float8': 1.2345678901234567890,
        'decimal': 12345678901234567890,
        'text': 'Hello',
        'timestamp': datetime.datetime.now()
    } 
    q = test_base.insert_test_table_encrypted(mindlake, tableNameAlice, data)
   
    cocoonName = "test_cocoon_alice_encrypted" 
    test_base.create_test_cocoon(mindlake, cocoonName)
    code = test_base.link_table_to_cocoon_test(mindlake, tableNameAlice, cocoonName)
    assert code == 0, "alice can not link her table to her cocoon !"

def test_link_table_to_otherwalletcocoon_bob_encrypted(mindlake: MindLake):
    print_test_functions()
   
    tableNameAlice = 'test_table_encrypted_Alice' 
    cocoonName = "test_cocoon_bob_encrypted" 
    test_base.create_test_cocoon(mindlake, cocoonName)
    code = test_base.link_table_to_cocoon_test(mindlake, tableNameAlice, cocoonName)
    assert code != 0, "bob can link alice's table to his cocoon !"
    # also need to check error code




print("============= link nonencrypted table ============")    
def test_link_table_to_mywalletcocoon_alice_nonencrypted(mindlake: MindLake):
    print_test_functions()
    
    tableNameAlice = 'test_table_nonencrypted_Alice'
    test_base.drop_test_table(mindlake, tableNameAlice)
    test_base.create_test_table_nonencrypted(mindlake, tableNameAlice)
    test_base.insert_test_table_nonencrypted(mindlake, tableNameAlice)
   
    cocoonName = "test_cocoon_alice_nonencrypted" 
    test_base.create_test_cocoon(mindlake, cocoonName)
    code = test_base.link_table_to_cocoon_test(mindlake, tableNameAlice, cocoonName)
    assert code == 0, "alice can not link her table to her cocoon !"

def test_link_table_to_otherwalletcocoon_bob_nonencrypted(mindlake: MindLake):
    print_test_functions()
   
    tableNameAlice = 'test_table_nonencrypted_Alice' 
    cocoonName = "test_cocoon_bob_nonencrypted" 
    test_base.create_test_cocoon(mindlake, cocoonName)
    code = test_base.link_table_to_cocoon_test(mindlake, tableNameAlice, cocoonName)
    assert code != 0, "bob can link alice's table to his cocoon !"
    # also need to check error code



print("============= link nonencrypted table ============") 
def test_unique_link(mindlake: MindLake):
    print_test_functions()
  
    cocoonName1 = "test_cocoon_alice_nonencrypted" 
    result = mindlake.datalake.listTablesByCocoon(cocoonName1)
    logging.warning('listTablesByCocoon: %s %s %s'%(cocoonName1, result.code, result.message))
    tables = result.data
    logging.debug(tables)
    tableNameAlice1 = 'test_table_nonencrypted_Alice' 
    assert tableNameAlice1 in tables, 'table should be linked to cocoon !'
    
    cocoonName2 = "test_cocoon_alice_encrypted" 
    result = mindlake.datalake.listTablesByCocoon(cocoonName2)
    logging.warning('listTablesByCocoon: %s %s %s'%(cocoonName2, result.code, result.message))
    tables = result.data
    logging.debug(tables)
    tableNameAlice2 = 'test_table_encrypted_Alice' 
    assert tableNameAlice2 in tables, 'table should be linked to cocoon !'

    code = test_base.link_table_to_cocoon_test(mindlake, tableNameAlice1, cocoonName2)
    cocoonName2 = "test_cocoon_alice_encrypted" 
    result = mindlake.datalake.listTablesByCocoon(cocoonName2)
    logging.warning('listTablesByCocoon: %s %s %s'%(cocoonName2, result.code, result.message))
    tables = result.data
    tableNameAlice1 = 'test_table_encrypted_Alice' 
    assert tableNameAlice1 in tables, 'table should be linked to other cocoon !' 
    
    cocoonName1 = "test_cocoon_alice_nonencrypted" 
    result = mindlake.datalake.listTablesByCocoon(cocoonName1)
    logging.warning('listTablesByCocoon: %s %s %s'%(cocoonName1, result.code, result.message))
    tables = result.data
    tableNameAlice1 = 'test_table_nonencrypted_Alice' 
    assert tableNameAlice1 not in tables, 'table should be linked to other cocoon and not exist in previous cocoon!'  
      

print("============= link non-existing table ============") 
def test_link_nonexist_table(mindlake: MindLake):
    print_test_functions()
  
    tableName = 'test_table_nonencrypted_nobody' 
    cocoonName = "test_cocoon_alice_encrypted" 

    code = test_base.link_table_to_cocoon_test(mindlake, tableName, cocoonName)
    
    assert code != 0, "non exist table can not be linked !"
    
    
print("============= link non-existing cocoon ============") 
def test_link_nonexist_cocoon(mindlake: MindLake):
    print_test_functions()
  
    tableName = 'test_cocoon_alice_encrypted' 
    cocoonName = "test_cocoon_nobody_encrypted" 

    code = test_base.link_table_to_cocoon_test(mindlake, tableName, cocoonName)
    
    assert code != 0, "non exist cocoon can not be linked !"
    


print("============= complete 4 ============")
def cases(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey):
    mindlakeAlice = mindlakesdk.connect(walletPrivateKeyAlice, appKey, env.GATEWAY)
    mindlakeBob = mindlakesdk.connect(walletPrivateKeyBob, appKey, env.GATEWAY)
    test_base.drop_all_cocoon_and_table(mindlakeAlice)
    test_base.drop_all_cocoon_and_table(mindlakeBob)

    test_link_table_to_mywalletcocoon_alice_encrypted(mindlakeAlice)
    test_link_table_to_mywalletcocoon_alice_nonencrypted(mindlakeAlice) 
    
    test_link_table_to_otherwalletcocoon_bob_nonencrypted(mindlakeBob)
    test_link_table_to_otherwalletcocoon_bob_encrypted(mindlakeBob)
    
    test_unique_link(mindlakeAlice)
    
    test_link_nonexist_table(mindlakeAlice)
    test_link_nonexist_cocoon(mindlakeAlice)
    
if __name__ == "__main__":
    cases(env.walletPrivateKeyAlice, env.walletPrivateKeyBob, env.walletAddressAlice, env.walletAddressBob, env.appKey)
    
