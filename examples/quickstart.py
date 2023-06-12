import env
import mindlakesdk
import logging

# logging.basicConfig(level=logging.DEBUG)

# 1. connect to MindLake
mindLake = mindlakesdk.connect(env.walletPrivateKeyAlice, env.appKey)
assert mindLake, mindLake.message

result = mindLake.datalake.dropTable('test_table_enc')

# 2. create a table
result = mindLake.datalake.createTable('test_table_enc',
        [
            mindLake.datalake.Column('id', mindLake.DataType.int4, False),
            mindLake.datalake.Column('token', mindLake.DataType.text, True)
        ])
assert result, result.message

# 3. encrypt data
result = mindLake.cryptor.encrypt('USDT','test_table_enc.token')
assert result, result.message
encryptedTokenName = result.data

# 4. insert encrypted data
result = mindLake.datalake.query(f"""INSERT INTO test_table_enc (id, token) 
VALUES (1, '{encryptedTokenName}')""")
assert result, result.message

# 5. query encrypted data
result = mindLake.datalake.query("SELECT token FROM test_table_enc")
assert result, result.message
print(result.data['columnList'][0])
for row in result.data['data']:
    result = mindLake.cryptor.decrypt(row[0])
    assert result, result.message
    print(result.data)
