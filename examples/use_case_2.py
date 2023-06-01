import env
import mindlakesdk
import requests
from base64 import a85decode, a85encode
from hashlib import md5

# 1. connect to MindLake
mindlake = mindlakesdk.connect(env.walletPrivateKeyBob, env.appKey)
assert mindlake, mindlake.message

result = mindlake.datalake.dropTable('album')

# 2. create a table
result = mindlake.datalake.createTable('album',
        [
            mindlake.datalake.Column('name', mindlake.DataType.text, False),
            mindlake.datalake.Column('picture', mindlake.DataType.text, True),
        ])
assert result, result.message

# 3. get a picture from github
response = requests.get('https://avatars.githubusercontent.com/u/97393721')
if response and response.status_code == 200:
    pic = response.content
else:
    raise Exception('Failed to get picture from github')

file = open('pic_origin.png', 'wb')
file.write(pic)
file.close()
print('MD5 of the original picture pic_origin.png: ' + md5(pic).hexdigest())

# 4. encrypt and insert the data
result = mindlake.cryptor.encrypt(a85encode(pic).decode(),'album.picture')
assert result, result.message
encryptedPic = result.data

result = mindlake.datalake.query(f"""
INSERT INTO "album" 
       ("name", "picture") 
VALUES ('{'mind.png'}',
        '{encryptedPic}') returning *""")
assert result, result.message

# 5. query encrypted data
result = mindlake.datalake.query('SELECT * FROM "album"')
assert result, result.message

# 6. decrypt the data
for row in result.data['data']:
    name = row[0]
    resultPic = mindlake.cryptor.decrypt(row[1])
    assert resultPic, resultPic.message
    decryptedPic = a85decode(resultPic.data)
    file = open(f'{name}', 'wb')
    file.write(decryptedPic)
    file.close()
    print(f'MD5 of the decrypted picture {name}: ' + md5(decryptedPic).hexdigest())
