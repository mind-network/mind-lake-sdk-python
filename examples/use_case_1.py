import env
import mindlakesdk
import logging

# logging.basicConfig(level=logging.DEBUG)

# 1. connect to mindlake
mindlake = mindlakesdk.connect(env.walletPrivateKeyBob, env.appKey)
assert mindlake, mindlake.message

result = mindlake.datalake.dropTable('wallet_balance')

# 2. create a table
result = mindlake.datalake.createTable('wallet_balance',
        [
            mindlake.datalake.Column('WalletAddress', mindlake.DataType.text, False),
            mindlake.datalake.Column('Name', mindlake.DataType.text, True),
            mindlake.datalake.Column('Balance', mindlake.DataType.float4, True)
        ],
        primaryKey=['WalletAddress'])
assert result, result.message

# 3. encrypt and insert the data
result = mindlake.cryptor.encrypt('Alice','wallet_balance.Name')
assert result, result.message
encryptedName = result.data
result = mindlake.cryptor.encrypt(10.5,'wallet_balance.Balance')
assert result, result.message
encryptedBalance = result.data

result = mindlake.datalake.query(f"""
INSERT INTO "wallet_balance" 
       ("WalletAddress", "Name", "Balance") 
VALUES ('{'0xB2F588A50E43f58FEb0c05ff86a30D0d0b1BF065'}',
        '{encryptedName}',
        '{encryptedBalance}') returning *""")
assert result, result.message

# 4. a compact way to encrypt and insert
result = mindlake.datalake.query(f"""
INSERT INTO "wallet_balance" ("WalletAddress", "Name", "Balance")
VALUES ('0x420c08373E2ba9C7566Ba0D210fB42A20a1eD2f8',
    '{mindlake.cryptor.encrypt('Bob','wallet_balance.Name').data}',
    '{mindlake.cryptor.encrypt(20.5,'wallet_balance.Balance').data}') returning *
""")
assert result, result.message

# 5. query all the encrypted data
result = mindlake.datalake.query('SELECT * FROM "wallet_balance"')
assert result, result.message

# 6. print encryption data from query result
print('The data stored in Mind Lake:')
print('-'*77)
print('|', result.data["columnList"][0], " "*28, '|', result.data["columnList"][1],
      " "*8, '|', result.data["columnList"][2], " "*5, '|')
print('-'*77)
for row in result.data['data']:
    print('|', row[0], '|', row[1][:10]+'...', '|', row[2][:10]+'...', '|')
print('-'*77)

# 7. query encrypted data with condition and decrypt the data
#   Note: the condition must be encrypted
result = mindlake.datalake.query(
    f'''SELECT * FROM "wallet_balance" WHERE "Balance" > \
        '{mindlake.cryptor.encrypt(15.0, mindlake.DataType.float4).data}' ''')
assert result, result.message

print()
print('The data after decryption:')
print('-'*66)
print('|', result.data["columnList"][0], " "*28, '|', result.data["columnList"][1],
      " "*3, '|', result.data["columnList"][2], '|')
print('-'*66)
for row in result.data['data']:
    walletAddress = row[0]
    resultName = mindlake.cryptor.decrypt(row[1])
    resultBalance = mindlake.cryptor.decrypt(row[2])
    assert resultName, resultName.message
    assert resultBalance, resultBalance.message
    print('|', walletAddress, '|', resultName.data, '\t|', resultBalance.data, '\t  |')
print('-'*66)
