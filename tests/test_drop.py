from test_base import *

import test_base
#test_base.drop_all_cocoon_and_table(env.walletPrivateKey)

import logging
setLogging(logging.INFO)
#setLogging(logging.DEBUG)

import env
# logging.warning('walletPrivateKey = %s'%env.walletPrivateKey)

import mindlakesdk
print("============= start test ============")



def prepare_test(mindlake: MindLake):
    tableName = 'test_table_nonencrypted'
    test_base.drop_test_table(mindlake, tableName)
    test_base.create_test_table_nonencrypted(mindlake, tableName)
    test_base.insert_test_table_nonencrypted(mindlake, tableName)
    
    cocoonName = 'test_cocoon_create'
    test_base.create_test_cocoon(mindlake, cocoonName)
    test_base.link_table_to_cocoon_test(mindlake, tableName, cocoonName)

# by now, I should have at least one table and one cocoon, and table link to cocoon
print("============= test preparation completed ============")

def test_drop_cocoon_nonempty(mindlake: MindLake):
    print_test_functions
    
    prepare_test(mindlake)
    cocoonName = 'test_cocoon_create'
    code, data = test_base.drop_test_cocoon(mindlake, cocoonName)
    print(code, data)
    assert code == 40013, 'non-empty cocoon can not be dropped !'
    
def test_drop_table(mindlake: MindLake):
    print_test_functions
    
    prepare_test(mindlake)
    tableName = 'test_table_nonencrypted'
    code, data = test_base.drop_test_table(mindlake, tableName)
    assert code == 0 and data == True, 'table has problems to drop !' 

def test_drop_cocoon(mindlake: MindLake):
    print_test_functions
    
    cocoonName = 'test_cocoon_create'
    code, data= test_base.drop_test_cocoon(mindlake, cocoonName)
    assert code == 0 and data == True, 'empty cocoon has problems to drop !'


print("============= complete test ============")   
def cases(walletPrivateKey, appKey):
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey, env.GATEWAY)
    assert mindlake, 'mindlakesdk.connect failed !'
    test_base.drop_all_cocoon_and_table(mindlake)
    test_drop_cocoon_nonempty(mindlake)
    test_drop_table(mindlake)
    test_drop_cocoon(mindlake)
    
if __name__ == "__main__":
    cases(env.walletPrivateKey, env.appKey)
