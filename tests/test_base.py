#### set path to load source code ####
import os
import sys
import inspect
import logging
#logging.info("========== set path ===========") 

#### load MindLake from source code ####
from mindlakesdk import MindLake
#logging.info('MindLake Path: %s', mindlake.__path__)
#logging.info("========== load MindLake ===========")

#### load logging ####
import logging
#mindlake.utils.setLogging(logging.INFO)
#logging.info("========== load logging ===========")

#### load env ####
import env
#logging.info("========== load env ===========")

import unittest
from pprint import pprint
import datetime

logging.info("========== load test base ===========")

import colorlog 
import sys
import os

def setLogging(logginglevel):
    root = logging.getLogger()
    if len(root.handlers): ### ensure only one logging handler is added
        logging.debug("multiple logging exists")
        root.handlers.clear()
    root.setLevel(logginglevel)
        
    format      = '%(asctime)s|%(levelname)-8s |: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
              log_colors = { 'DEBUG'   : 'cyan',       'INFO' : 'green',
                             'WARNING' : 'bold_red', 'ERROR': 'bold_red',
                             'CRITICAL': 'bold_red' })
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)

def print_test_functions():
    logging.info(('******* test | %s *******'%(inspect.stack()[1][3])))

################################################
def drop_all_cocoon_and_table(mindlake: MindLake):    
    # additional test is to drop all cocoon and tables
    logging.info("==== test to drop all cocoon and table | start =====")

    result = mindlake.datalake.listCocoon()
    logging.info('listCocoon: %s %s'%(result.code, result.message))
    logging.debug(result.data)

    cocoonToDrop = {}
    cocoons = result.data
    if cocoons == None:
        cocoons = [] 
    for cocoon in cocoons:
        cocoonName = cocoon['cocoonName']
        cocoonToDrop[cocoonName] = {}
        result = mindlake.datalake.listTablesByCocoon(cocoonName)
        logging.info('listTablesByCocoon: %s %s %s'%(cocoonName, result.code, result.message))
        tables = result.data
        logging.debug(tables)
        for table in tables:
            cocoonToDrop[cocoonName][table] = {}
    
    logging.info("===== show cocoon and tables to drop =====")     
    logging.debug(cocoonToDrop)

    cocoonDropTableNonEmpty = {}
    cocoonDropped = {}
    tableDropped = {}

    for cocoonName in cocoonToDrop:
        if len(cocoonToDrop[cocoonName]) > 0:
            result = mindlake.datalake.dropCocoon(cocoonName)
            logging.info('dropCocoon: %s %s %s'%(cocoonName, result.code, result.message))
            logging.debug(result.data)
            if result:
                cocoonDropTableNonEmpty[cocoonName] = {}
            
            for tableName in cocoonToDrop[cocoonName]:
                result = mindlake.datalake.dropTable(tableName)
                logging.info('dropTable: %s %s %s'%(tableName, result.code, result.message))
                logging.debug(result.data)
                if not result:
                    tableDropped[table] = {}
        
        result = mindlake.datalake.dropCocoon(cocoonName)
        
        logging.info('dropCocoon: %s %s'%(cocoonName, result.code))
        logging.debug(result.data)
        if result:
            cocoonDropped[cocoonName] = {} 
            
    logging.info("==== all and cacoon are deleted ====")
    
    
    
################################################
def drop_test_table(mindlake: MindLake, tableName):
    result = mindlake.datalake.dropTable(tableName)
    logging.info('dropTable: %s %s %s'%(tableName, result.code, result.message))
    logging.debug(result.data)
    return result.code, result.data



################################################
def create_test_table_nonencrypted(mindlake: MindLake, tableName):
    columns = []
    columns.append(mindlake.datalake.Column('mid', mindlake.DataType.text, False))
    columns.append(mindlake.datalake.Column('name', mindlake.DataType.text, False))
    columns.append(mindlake.datalake.Column('age', mindlake.DataType.text, False))
    logging.debug(columns)
    result = mindlake.datalake.createTable(tableName, columns)
    logging.info('createTable: %s %s %s'%(tableName, result.code, result.message))
    logging.debug(result.data)
    return result.code

def create_test_table_nonencrypted_unique(mindlake: MindLake, tableName):
    columns = []
    columns.append(mindlake.datalake.Column('mid', mindlake.DataType.text, False))
    columns.append(mindlake.datalake.Column('name', mindlake.DataType.text, False))
    columns.append(mindlake.datalake.Column('age', mindlake.DataType.text, False))
    logging.debug(columns)
    primarykeys = ['mid', 'name']
    logging.debug(primarykeys)
    result = mindlake.datalake.createTable(tableName, columns, primarykeys)
    logging.info('createTable: %s %s %s'%(tableName, result.code, result.message))
    logging.debug(result.data)
    return result.code

def create_test_table_encrypted(mindlake: MindLake, tableName):
    columns = []
    columns.append(mindlake.datalake.Column('dataint4', mindlake.DataType.int4, True))
    columns.append(mindlake.datalake.Column('dataint8', mindlake.DataType.int8, True))
    columns.append(mindlake.datalake.Column('datafloat4', mindlake.DataType.float4, True))
    columns.append(mindlake.datalake.Column('datafloat8', mindlake.DataType.float8, True))
    columns.append(mindlake.datalake.Column('datadecimal', mindlake.DataType.decimal, True))
    columns.append(mindlake.datalake.Column('datatext', mindlake.DataType.text, True))
    columns.append(mindlake.datalake.Column('datatimestamp', mindlake.DataType.timestamp, True))
    logging.debug(columns)
    result = mindlake.datalake.createTable(tableName, columns)
    logging.info('createTable: %s %s %s'%(tableName, result.code, result.message))
    logging.debug(result.data)
    return result.code

def create_test_table_encrypted_unique(mindlake: MindLake, tableName):
    columns = []
    columns.append(mindlake.datalake.Column('dataint4', mindlake.DataType.int4, True))
    columns.append(mindlake.datalake.Column('dataint8', mindlake.DataType.int8, True))
    columns.append(mindlake.datalake.Column('datafloat4', mindlake.DataType.float4, True))
    columns.append(mindlake.datalake.Column('datafloat8', mindlake.DataType.float8, True))
    columns.append(mindlake.datalake.Column('datadecimal', mindlake.DataType.decimal, True))
    columns.append(mindlake.datalake.Column('datatext', mindlake.DataType.text, True))
    columns.append(mindlake.datalake.Column('datatimestamp', mindlake.DataType.timestamp, True))
    logging.debug(columns)
    primarykeys = ['dataint4']
    logging.debug(primarykeys)
    result = mindlake.datalake.createTable(tableName, columns, primarykeys)
    logging.info('createTable: %s %s %s'%(tableName, result.code, result.message))
    logging.debug(result.data)
    return result.code




################################################
def insert_test_table_nonencrypted(mindlake: MindLake, tableName):
    # insert one raw
    sql = f"""INSERT INTO "{tableName}" (mid, name, age) VALUES ('a1', 'b1', 'c1') RETURNING *"""
    logging.debug(sql)
    q = mindlake.datalake.query(sql)
    logging.info('Query: Code: %s %s %s', q.code, q.message, sql)
    assert q, q.message
    logging.debug(q.data)
   
    # insert second raw 
    sql = f"""INSERT INTO "{tableName}" (mid, name, age) VALUES ('a1', 'b1', 'c1') RETURNING *"""
    logging.debug(sql)
    q = mindlake.datalake.query(sql)
    logging.info('Query: Code: %s %s %s', q.code, q.message, sql)
    logging.debug(q.data)
    
    #print("===== select * =====")
    sql = f"""SELECT * FROM "{tableName}" """
    logging.debug(sql)
    q = mindlake.datalake.query(sql)
    logging.info('Query: Code: %s %s %s', q.code, q.message, sql)
    logging.debug(q.data)
    count_select_all = len(q.data['data'])
        
    return count_select_all
        
        
def insert_test_table_encrypted(mindlake: MindLake, tableName, data):
    encryptedData = {}
    for k, v in data.items():
        logging.info(f"===== encrypt {k} in column =====")
        currentColumn = 'data' + k
        q = mindlake.cryptor.encrypt(v, f'{tableName}.{currentColumn}')
        logging.debug('Code: %s %s %s', q.code, q.message, f'encrypt {k}')
        assert q and isinstance(q.data, str) and q.data[:2] == '\\x', 'encryption test failed !'
        encryptedData[currentColumn] = q.data

    sql = f"""INSERT INTO "{tableName}" 
    VALUES (
        '{encryptedData['dataint4']}',
        '{encryptedData['dataint8']}',
        '{encryptedData['datafloat4']}',
        '{encryptedData['datafloat8']}',
        '{encryptedData['datadecimal']}',
        '{encryptedData['datatext']}',
        '{encryptedData['datatimestamp']}') RETURNING *"""
    logging.debug(sql)
    q = mindlake.datalake.query(sql)
    logging.debug('Code: %s %s %s', q.code, q.message, 'INSERT')
    return q


################################################
def update_test_table_nonencrypted(mindlake: MindLake, tableName):
    # insert one raw
    sql = f"""UPDATE "{tableName}" SET name = 'b11', age = 'c11' WHERE mid = 'a1' RETURNING *"""
    logging.debug(sql)
    q = mindlake.datalake.query(sql)
    logging.info('Query Code: %s %s %s', q.code, q.message, sql)
    logging.debug(q.data)
    
    logging.info("===== select * =====")
    sql = f"SELECT * FROM {tableName} WHERE mid = 'a1'"
    q = mindlake.datalake.query(sql)
    logging.info('Query Code: %s %s %s', q.code, q.message, sql)
    assert q, q.message
    logging.debug(q.data) 
    return q.data['data']

def update_test_table_encrypted(mindlake: MindLake, tableName, data, index):
    encryptedData = {}
    for k, v in data.items():
        logging.info(f"===== encrypt {k} in column =====")
        currentColumn = 'data' + k
        q = mindlake.cryptor.encrypt(v, f'{tableName}.{currentColumn}')
        logging.debug('Code: %s %s %s', q.code, q.message, f'encrypt {k}')
        assert q and isinstance(q.data, str) and q.data[:2] == '\\x', 'encryption test failed !'
        encryptedData[currentColumn] = q.data

    q = mindlake.cryptor.encrypt(index, mindlake.DataType.int4)
    assert q, q.message
    encryptedIndex = q.data

    sql = f"""UPDATE {tableName} 
    SET 
        dataint8 = '{encryptedData['dataint8']}',
        datafloat4 = '{encryptedData['datafloat4']}',
        datafloat8 = '{encryptedData['datafloat8']}',
        datadecimal = '{encryptedData['datadecimal']}',
        datatext = '{encryptedData['datatext']}',
        datatimestamp = '{encryptedData['datatimestamp']}'
    WHERE 
        dataint4 = '{encryptedIndex}'
    RETURNING *"""
    logging.debug(sql)
    q = mindlake.datalake.query(sql)
    logging.info('Query Code: %s %s %s', q.code, q.message, sql)
    assert q, q.message
    return q


################################################
def link_table_to_cocoon_test(mindlake: MindLake, tableName, cocoonName):
    result = mindlake.datalake.linkTableToCocoon(tableName, cocoonName)
    logging.info('linkTableToCocoon: %s->%s %s %s'%(tableName, cocoonName, result.code, result.message))
    logging.debug(result.data)
    return result.code

def create_test_cocoon(mindlake: MindLake, cocoonName):
    result = mindlake.datalake.createCocoon(cocoonName)
    logging.info('createCocoon: %s %s %s'%(cocoonName, result.code, result.message))
    logging.debug(result.data)
    return result.code

def drop_test_cocoon(mindlake: MindLake, cocoonName):
    result = mindlake.datalake.dropCocoon(cocoonName)
    logging.info('dropCocoon: %s %s %s'%(cocoonName, result.code, result.message))
    logging.debug(result.data)
    return result.code, result.data


################################################
def check_coocoon_exists(result, cocoonName):
    found = False
    if result == None:
        return found
    for r in result:
        if r['cocoonName'] == cocoonName:
            found = True
            break
    #print(found)
    return found

def check_table_exists(result, tableName):
    return tableName in result


def check_grantee_exists(result, walletAddress):
    return walletAddress in result


def check_column_exists(result, columnName):
    return columnName in result  
   
            
    