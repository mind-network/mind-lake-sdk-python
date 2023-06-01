import env
import mindlakesdk
import logging

logging.basicConfig(level=logging.DEBUG)

# the policy grant target should be an existing user in MindLake, so first register Charlie
mindlake = mindlakesdk.connect(env.walletPrivateKeyCharlie, env.appKey)
assert mindlake, mindlake.message

def writeDataGrantToCharlie(walletPrivateKey, appKey, data) -> str:
    # connect to MindLake
    mindlake = mindlakesdk.connect(walletPrivateKey, appKey)
    assert mindlake, mindlake.message

    result = mindlake.datalake.dropTable('transaction_temp')

    # create a table
    result = mindlake.datalake.createTable('transaction_temp',
            [
                mindlake.datalake.Column('WalletAddress', mindlake.DataType.text, True),
                mindlake.datalake.Column('Token', mindlake.DataType.text, True),
                mindlake.datalake.Column('Volume', mindlake.DataType.float4, True)
            ])
    assert result, result.message

    # encrypt and insert
    for row in data:
        result = mindlake.datalake.query(f"""
        INSERT INTO "transaction_temp" ("WalletAddress", "Token", "Volume")
        VALUES (
            '{mindlake.cryptor.encrypt(row["wallet"],'transaction_temp.WalletAddress').data}',
            '{mindlake.cryptor.encrypt(row["token"],'transaction_temp.Token').data}',
            '{mindlake.cryptor.encrypt(row["volume"],'transaction_temp.Volume').data}')
        """)
        assert result, result.message

    result = mindlake.permission.grant(env.walletAddressCharlie,
        ['transaction_temp.WalletAddress', 'transaction_temp.Token', 'transaction_temp.Volume'])
    assert result, result.message
    policyID = result.data
    return policyID

# Alice write data to table and grant permission to Charlie    
policyIDAlice = writeDataGrantToCharlie(env.walletPrivateKeyAlice, env.appKey, [
    {'wallet': '0x8CFB38b2cba74757431B205612E349B8b9a9E661', 'token': 'USDT', 'volume': 5.6},
    {'wallet': '0xD862D48f36ce6298eFD00474eC852b8838a54F66', 'token': 'BUSD', 'volume': 6.3},
    {'wallet': '0x8CFB38b2cba74757431B205612E349B8b9a9E661', 'token': 'BUSD', 'volume': 10.3}
])

# Bob write data to table and grant permission to Charlie
policyIDBob = writeDataGrantToCharlie(env.walletPrivateKeyBob, env.appKey, [
    {'wallet': '0xD862D48f36ce6298eFD00474eC852b8838a54F66', 'token': 'USDT', 'volume': 3.3},
    {'wallet': '0x70dBcC09edF6D9AdD4A235e2D8346E78A79ac770', 'token': 'BUSD', 'volume': 9.8},
    {'wallet': '0x70dBcC09edF6D9AdD4A235e2D8346E78A79ac770', 'token': 'USDT', 'volume': 7.7}
])

# Charlie confirm the permission
mindlake = mindlakesdk.connect(env.walletPrivateKeyCharlie, env.appKey)
assert mindlake, mindlake.message
result = mindlake.permission.confirm(policyIDAlice)
assert result, result.message
result = mindlake.permission.confirm(policyIDBob)
assert result, result.message

# Charlie query and calculate the total volume of each wallet
result = mindlake.datalake.query(f'''
SELECT combine."WalletAddress", SUM(combine."Volume") FROM
(SELECT "WalletAddress","Volume" FROM "{env.walletAddressAlice[2:].lower()}"."transaction_temp"
UNION ALL
SELECT "WalletAddress","Volume" FROM "{env.walletAddressBob[2:].lower()}"."transaction_temp") as combine
GROUP BY "WalletAddress"
''')
assert result, result.message

print('-'*57)
print('|', result.data["columnList"][0], " "*28, '|', result.data["columnList"][1], '\t|')
print('-'*57)
for row in result.data['data']:
    result = mindlake.cryptor.decrypt(row[0])
    assert result, result.message
    walletAddress = result.data
    result = mindlake.cryptor.decrypt(row[1])
    assert result, result.message
    sumVolume = result.data
    print(f'| {walletAddress} | {sumVolume:.1f}\t|')
print('-'*57)
