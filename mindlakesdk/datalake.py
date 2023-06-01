from mindlakesdk.utils import ResultType, Session, DataType
import mindlakesdk.message
import logging

class DataLake:
    def __init__(self, session: Session):
        self.__session = session

    class Column(dict):
        def __init__(self, columnName: str, dataType: DataType, encrypt: bool):
            self.columnName = columnName
            self.type = dataType
            self.encrypt = encrypt
        
        def toDict(self):
            return {
                'columnName': self.columnName,
                'type': self.type.value,
                'encrypt': self.encrypt
            }

    def createTable(self, tableName: str, columns: list, primaryKey: list = None) -> ResultType:
        columnsDict = []
        for column in columns:
            columnsDict.append(column.toDict())
        return mindlakesdk.message.sendCreateTable(self.__session, tableName, columnsDict, primaryKey)
    
    def listCocoon(self) -> ResultType:
        logging.debug("listCocoon")
        return mindlakesdk.message.sendListCocoon(self.__session)
    
    def linkTableToCocoon(self, tableName: str, cocoonName: str) -> ResultType:
        return mindlakesdk.message.sendLinkTableToCocoon(self.__session, tableName, cocoonName) 
    
    def listTablesByCocoon(self, cocoonName: str) -> ResultType:
        return mindlakesdk.message.sendListTablesByCocoon(self.__session, cocoonName) 
    
    def createCocoon(self, cocoonName: str) -> ResultType:
        return mindlakesdk.message.sendCreateCocoon(self.__session, cocoonName) 
    
    def query(self, executeSql: str) -> ResultType:
        return mindlakesdk.message.sendQuery(self.__session, executeSql)
    
    def dropCocoon(self, cocoonName: str) -> ResultType:
        return mindlakesdk.message.sendDropCocoon(self.__session, cocoonName)
    
    def dropTable(self, tableName: str) -> ResultType:
        return mindlakesdk.message.sendDropTable(self.__session, tableName)  
    