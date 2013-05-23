'''
This module encapulate the operations to sqlite in an engine.

'''
import sqlite3
class SLEngine:
    def __init__(self, dbfile):
        self.__connection__ = self._connect(dbfile)
    
    def _connect(self, dbfile):
        return sqlite3.connect(dbfile)
        
    def _getConnection(self):
        return self.__connection__
    
    def _query(self, sql_query):
     
        con = self._getConnection()
        cursor = con.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        #cursor.close()
        return result
    
    #External interfaces
    def getFIELDLIST(self, table):
        return map(lambda x:x[0], self._query('''select FIELD from %s'''%table))
        
    def getVALUELIST(self, table, fieldName):
        #return self._query('select VALUELIST from %s where FIELD='%(table, fieldName))
        r = self._query("select VALUELIST from %s where FIELD='%s'"%(table, fieldName))[0][0]
        if r:
            return  r.split(',')
        return []
        
                                                       
    def getGROUPLIST(self, table, fieldName):
        r = self._query("select GROUPLIST from %s where FIELD='%s'"%(table, fieldName))[0][0]
        if r:
            return  r.split(',')
        return []
    
  
        
if __name__ == "__main__":
    e = SLEngine('db\data.db3')
    print e.getSTATGROUP('mms',   'RECVER')
    #print e.getFIELDLIST('mms')
    #print e._query('select SECTION from numbersection')  
