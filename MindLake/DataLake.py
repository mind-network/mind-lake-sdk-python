from MindLake.utils import ResultType, Session, DataType
import MindLake.message
import logging

class DataLake:

    __session = None

    def setSession(session: Session):
        DataLake.__session = session

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

    def createTable(tableName: str, columns: list, primaryKey: list = None) -> ResultType:
        columnsDict = []
        for column in columns:
            columnsDict.append(column.toDict())
        return MindLake.message.sendCreateTable(DataLake.__session, tableName, columnsDict, primaryKey)
    
    def listCocoon() -> ResultType:
        logging.debug("listCocoon")
        return MindLake.message.sendListCocoon(DataLake.__session)
    
    def linkTableToCocoon(tableName: str, cocoonName: str) -> ResultType:
        return MindLake.message.sendLinkTableToCocoon(DataLake.__session, tableName, cocoonName) 
    
    def listTablesByCocoon(cocoonName: str) -> ResultType:
        return MindLake.message.sendListTablesByCocoon(DataLake.__session, cocoonName) 
    
    def createCocoon(cocoonName: str) -> ResultType:
        return MindLake.message.sendCreateCocoon(DataLake.__session, cocoonName) 
    
    def query(executeSql: str) -> ResultType:
        return MindLake.message.sendQuery(DataLake.__session, executeSql)
    
    def dropCocoon(cocoonName: str) -> ResultType:
        return MindLake.message.sendDropCocoon(DataLake.__session, cocoonName)
    
    def dropTable(tableName: str) -> ResultType:
        return MindLake.message.sendDropTable(DataLake.__session, tableName)  
    