import env
import mindlakesdk
import logging

# logging.basicConfig(level=logging.DEBUG)

# 1. connect to MindLake
mind = mindlakesdk.connect(env.walletPrivateKeyAlice, env.appKey)
assert mind, mind.message

result = mind.datalake.dropTable('test_table_enc')

# 2. create a table
result = mind.datalake.createTable('test_table_enc',
        [
            mind.datalake.Column('id', mind.DataType.int4, False),
            mind.datalake.Column('token', mind.DataType.text, True)
        ])
assert result, result.message

# 3. encrypt data
result = mind.cryptor.encrypt('USDT','test_table_enc.token')
assert result, result.message
encryptedTokenName = result.data

# 4. insert encrypted data
result = mind.datalake.query(f"""INSERT INTO test_table_enc (id, token) 
VALUES (1, '{encryptedTokenName}')""")
assert result, result.message

# 5. query encrypted data
result = mind.datalake.query("SELECT token FROM test_table_enc")
assert result, result.message
print(result.data['columnList'][0])
for row in result.data['data']:
    result = mind.cryptor.decrypt(row[0])
    assert result, result.message
    print(result.data)
