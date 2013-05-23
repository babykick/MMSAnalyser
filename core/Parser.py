#coding=utf-8
import datetime
import itertools
from PyQt4.QtGui import QTableWidgetItem
import codecs
from core.utils import calTimeSpent
 
class Reader: 
    def __init__(self, head, files, delimiter=','):
        self.head = head
        self.files = files             #;print self.files        
        self.delimiter = delimiter
        
    def read(self):
        raise NotImplementedError()
        
class NewspaperReader(Reader):        
    def read(self):
        '''Return the lines iterator read from the files.
        '''        
        def getIterDS():
            '''A generator  read from the files.
            '''
            for file in self.files:
                print 'reading', file
                for line in open(file):
                    try:
                        yield line.strip().decode('gb2312').split(self.delimiter)
                    except:
                        print 'problem line'
                        continue
                        
                     
        return TableSet(self.head, getIterDS())
    
class MMSReader(Reader):
    def read(self):
        '''Return the lines iterator read from the files.
        '''        
        def getIterDS():
            '''A generator  read from the files.
            '''
            for file in self.files:
                print 'reading', file
                for line in open(file):
                    try:
                        row = line.strip().decode('gb2312').split(self.delimiter)
                    except:
                        print 'problem line'
                        continue
                    if not row[1].startswith('0086'):
                        #print 'no',row
                        row[0],row[1] = row[1], row[0]
                        
                    yield row
                     
        return TableSet(self.head, getIterDS())    
    

class DataCenter:
    codeSuccess = None
    @classmethod
    def ResetData(cls, fileType):
        if fileType == 'mms':
            cls.codeSuccess = set(['1000', '4446','6015','6215','6315','2000','2001'])
        elif fileType =='newspaper':
            cls.codeSuccess = set(['1000', '4446'])
            
 
    
                                
class Mapper:
    '''Define a bunch of class methods to map the field value to required result'''
    localset = set([l.strip() for l in codecs.open(r'config/NumberSection.txt', encoding='gb2312')])
    branchDict = None
    
     
    @classmethod
    def getMapFunc(cls, field, value, flag):
        if not flag:
            return cls.mapNothing
        elif flag:          
            if field == u'接收方':
                if value == u'岳阳所有':
                    return cls.mapNumberToLocal
                else:
                    return cls.mapNumberToBranchName
            
            elif field == u'接收代码':
                return cls.mapCode 
                
            elif field == u'发送方':
                return cls.mapServiceType
            
       
        
    @classmethod
    def mapNothing(cls, v):
        return v
        
    @classmethod    
    def mapServiceType(self,  v):
        return u'点对点' if v.startswith('0086') else u'业务下发'
    
    @classmethod
    def mapNumberToLocal(cls, v):
        sec = v[-11:-4]    
        return u'岳阳所有' if  sec in cls.localset else None
                 
    @classmethod
    def mapNumberToBranchName(cls, v):
        #It should be local number 
        if cls.mapNumberToLocal(v):
            bd = cls.getBranchDict()
            number = v[-11:] 
            #print n
            for branch, numberset in bd.iteritems():
                if number in numberset:
                    return branch
                    break
        return ''
        
    @classmethod
    def mapCode(cls, v):
        if v in DataCenter.codeSuccess:   
            return u'成功'
        else:
            return u'失败'
   
    @classmethod
    def getBranchDict(cls):
        if not cls.branchDict:
            starttime = datetime.datetime.now()
            d= {}
            for line in open(r'config/Branch.txt'):
                number, branch = line.split('\t')
                branch = branch.strip().decode('gb2312')
                d.setdefault(branch, set())
                d[branch].add(number)
            cls.branchDict = d
            print 'building branch dict', ( datetime.datetime.now()- starttime).seconds,'seconds used'
        return cls.branchDict

class Filter:
    '''select the fields'''
    def __init__(self, fieldName, fieldID, value, mapflag=False):
        self.fieldID = fieldID      
        self.mapfunc = Mapper.getMapFunc(fieldName, value, mapflag)
        self.value = value                                         
        
    def isPredicateRow(self, row):
        '''
        Select the row which satisfy the given key-value pairs.
        '''
        return self.extractMappedValue(row) == self.value
        
    def extractMappedValue(self, row):
        return self.mapfunc(row[self.fieldID])
                      
class TableSet:
    '''Store the table dataset'''
    def __init__(self, header, dataset):
        self.header = header
        self.dataset = dataset
    
    def head(self):
        return self.header
    
    def headIndex(self, section):
        return self.header.index(section)
    
    def getDataset(self):
        return self.dataset

    def setDataset(self, ds):
        self.dataset = ds


class Statist:
    '''Define a sketlon for statistics'''
    def __init__(self, tableSet, field, value, mapflag):
        self.tableSet = tableSet
        self.keyFilter = Filter(field, tableSet.headIndex(field), value, mapflag) 
        self.extend_map = Mapper.getMapFunc(field, value, True)
        self.targetValue = value
 
    def summary(self):
        ''' Convert the summary dict:
            {key1:{k1:v1,k2:v2},
             key2:{k1:v1,k2:v2},
             key3:{k1:v1,k2:v2}
            }
            To a plain table:
             [[statpoint, k1, k2],
             [key1, v1, v2]
             [key1, v1, v2]
             ]    
        '''
        
        stDict = self.doSummary() 
        for k, st in stDict.iteritems():
            #extend the keyfield
            st.update({'statpoint': k})
            #extend the caculating field
            st.update({'extend': self.extend_map(k)})
            
        #self.stDict = stDict
        return self.genTableSet(stDict)
         
            
    def genTableSet(self, stDict):
                 
        dictTable = stDict.itervalues()  
        try:
            line = dictTable.next()
        except:
            print 'empty result'
            return TableSet([],[])
        header = line.keys()
        dataset = itertools.chain([line.values()], itertools.imap(lambda r:r.values(), dictTable))
        return TableSet(header, dataset)
        


class StatistMMS(Statist):
    '''Perform statist by given field.
       Use the processor and reporter object to statist '''

    sizethres = 40  #The mms size (Bytes)
    timethres = 60  #The mms transfer time (seconds)
    specifiedSender = '801177'
    specifiedCode = '1000'
     
    def doSummary(self):
        codeMapper = Mapper.getMapFunc(u'接收代码', '', True)
        print 'statist mms use code mapper:', codeMapper
        stDict = {}
        for row in  self.tableSet.getDataset():  
            #we know the schema 
            if len(row) == 6: 
                serveCode, Number, recCode, size, timeStart, timeEnd = row 
                if not Number.startswith('0086'):
                    serveCode, Number = Number, serveCode
            else:
                continue    
            summaryField = self.keyFilter.extractMappedValue(row)  #which one is the summary key
            #print summaryField,' -- ',self.targetValue
            if  not summaryField: continue
            if self.targetValue != u'全选':
                if summaryField != self.targetValue:continue
            #summaryField = summaryField.encode('gb2312')
            stDict.setdefault(summaryField, {'count':0, 'sum_size':0, 'sum_time':0, 'suc_cnt':0, 'sender_codes':''})    
            stDict[summaryField]['count'] += 1

            if codeMapper(recCode) == u'成功': 
                stDict[summaryField]['suc_cnt'] += 1
                if recCode == self.specifiedCode:# and serveCode == self.specifiedSender:
                    size, elapseTime = int(size),  calTimeSpent(timeStart,timeEnd)
                    if size > self.sizethres and elapseTime <= self.timethres:
                        stDict[summaryField]['sum_size'] += size
                        stDict[summaryField]['sum_time'] += elapseTime
            
            #接收代码汇总           
            stDict[summaryField]['sender_codes'] += serveCode + ';'
            
                
        for st in stDict.itervalues():
            st.update({
                       'aver_size(Byte)':str(round(float(st['sum_size'])/st['count'], 2)),
                       'aver_time(s)':str(round(float(st['sum_time'])/st['count'], 2)),
                       'aver_speed(Kb/s)':str(round(st['sum_size']*8 / 1024.0 / st['sum_time'], 2)) if st['sum_time'] else 0,
                       'suc_rate':str(round(float(st['suc_cnt'])/st['count']*100, 2)) + '%'
                             })
        return stDict     
    

class StatistNewspaper(Statist):
    '''Perform statist by given field.
       Use the processor and reporter object to statist '''
  
    def doSummary(self):
        codeMapper = Mapper.getMapFunc(u'接收代码', '', True)
        print 'stastist newspaper use code mapper:', codeMapper
        stDict = {}
        for row in self.tableSet.getDataset():
            summaryField = self.keyFilter.extractMappedValue(row) #which one is the summary key
            if  not summaryField: continue
            if self.targetValue != u'全选':
                if summaryField != self.targetValue:continue
            if len(row) == 3:
                number, serveCode, recCode = row 
            else:continue
            stDict.setdefault(summaryField, {'count':0, 'suc_cnt':0, 'sender_codes':''})
            stDict[summaryField]['count'] += 1
            if codeMapper(recCode) == u'成功':
                stDict[summaryField]['suc_cnt'] += 1
            
            #接收代码汇总 
            stDict[summaryField]['sender_codes'] += serveCode + ';'
 
        for  st in stDict.itervalues():
            st.update({'suc_rate':str(round(float(st['suc_cnt'])/st['count']*100, 2)) + '%' if st['count'] else 0})
             
        return stDict  
    
     
       
'''
===========MVC Pattern========================
'''        
class AnalyseModel:
    def __init__(self):
        self.tableSet = None
        self.filterList = []
        self.statist = None
        self.viewList = []
             
    def run(self): 
        self.applyFilter(self.tableSet)
        if self.statist:
            self.tableSet = self.statist.summary()
        for v in self.viewList:
            v.update(self.tableSet)
    
    def setReader(self, readerConfig):
        DataCenter.ResetData(readerConfig['type'])
        print DataCenter.codeSuccess
        if readerConfig['type'] == 'mms':
            reader = MMSReader([u'发送方', u'接收方', u'接收代码', u'大小', u'开始时间', u'结束时间'],
                                  readerConfig['files'],
                                  ',')
        elif readerConfig['type'] == 'newspaper':
            reader = NewspaperReader([u'接收方', u'发送方', u'接收代码'],
                                  readerConfig['files'],
                                 ',')
            
        self.tableSet = reader.read()    

            
    def addFilter(self, filterConfig):
        f = Filter(filterConfig['field'], self.tableSet.headIndex(filterConfig['field']), filterConfig['value'], filterConfig['flag'])
        self.filterList.append(f)  
               
    def applyFilter(self, ts):  
        iterDS = ts.getDataset()
        for ft in self.filterList:
            iterDS = itertools.ifilter(ft.isPredicateRow, iterDS)
            
        ts.setDataset(iterDS)
        
             
    def setStatist(self, statistConfig):
        if statistConfig['type'] == 'mms':
            self.statist = StatistMMS(self.tableSet, statistConfig['field'], statistConfig['value'], statistConfig['flag'])
        elif statistConfig['type'] == 'newspaper':
            self.statist = StatistNewspaper(self.tableSet, statistConfig['field'],  statistConfig['value'], statistConfig['flag'])
            
    def addView(self, viewConfig):
        if viewConfig['type'] == 'display':
            if viewConfig['outlook'] == 'print':
                view = PrintView()
            elif viewConfig['outlook'] == 'pyqtTable':
                view = PyqtTableViewAdapter(viewConfig['ptable'])
        elif viewConfig['type'] == 'save':
            view = PersistView(viewConfig['file'])

        self.viewList.append(view)
        
    def saveToDatabase(self):
        pass
    
class TransactionControl:
    def __init__(self, transConfig):
        self.config = transConfig
        self.model = AnalyseModel()
    
    def setupModel(self):
        #Set the reader 
        if 'reader' in self.config:
            self.model.setReader(self.config['reader'])
        
        #Set the filter list    
        if 'filter' in self.config:
            for fConfig in self.config['filter']:
                self.model.addFilter(fConfig) 
                
        #Set the statist
        if 'statist' in self.config:     
            self.model.setStatist(self.config['statist'])
            
        #Set the view list
        if 'view' in self.config:   
            for vConfig in self.config['view']:
                self.model.addView(vConfig)        
        
    def execute(self):
        self.setupModel()     
        self.model.run()

class AbstractView:
    def update(self, resultSet):
        pass
    
class PyqtTableViewAdapter(AbstractView):
    '''
       Adapt to the external UI presentation.
    '''
    def __init__(self, pyqtTable):
        self.pyqtTable = pyqtTable
        
    def update(self, resultSet):
        h = resultSet.head()
        r = resultSet.getDataset()
        
        for i in range(len (h)):   
            a = QTableWidgetItem()
            a.setText(h[i])
            self.pyqtTable.setHorizontalHeaderItem(i, a)
            for j in range(len(r)):
                b = QTableWidgetItem()
                b.setText(unicode(str(r[j][i]),  'gb2312'))
                self.pyqtTable.setItem(j, i,  b)
        
class PrintView(AbstractView):
    def __init__(self):
        pass
        
    def update(self, resultTableSet):
        print 'result table'
        print resultTableSet.head()
        for i in resultTableSet.getDataset():
            print i

class PersistView(AbstractView):
    def __init__(self, fileName):
        self.saveFile = fileName

    def update(self, resultTableSet):
        if self.saveFile.endswith('.xls'):
            self.separate = u'\t'
        elif self.saveFile.endswith('.csv'):
            self.separate = u','
        elif self.saveFile.endswith('.txt'):
            self.separate = u'\t\t'
            
        print self.saveFile    
        outFile = open(self.saveFile, 'wb')
        outFile.write(self.separate.join(map(str, resultTableSet.head())) + '\n')
        for line in resultTableSet.getDataset(): 
            outFile.write(self.separate.join(map(unicode,  line)).encode('gb2312') + '\n')
        outFile.close()
            
            
if __name__ == "__main__":
    pass
#    m = AnalyseModel()
#    t = TransactionControl(None, m)
#    t.execute()
#    
    
 
  
