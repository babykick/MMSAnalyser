# -*- coding: utf-8 -*-

"""
Module implementing MainDialog.
"""
from PyQt4 import QtGui
from PyQt4.QtGui import QDialog,  QTableWidgetItem
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QMessageBox as msg
from Ui_MainWindow import Ui_MainDialog
#import sys  ;sys.path.append("..")
from PyQt4 import QtCore

from core.SliteManage import SLEngine  
from core import Parser


class MainDialog(QDialog, Ui_MainDialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initAll()
    
    def getFileType(self):
        if self.rbMMS.isChecked():
            return 'mms'
        elif self.rbNewspaper.isChecked():
            return 'newspaper'
        
    def initAll(self):
        self.sl = SLEngine('db/data.db3')
        self.updateFilterSetting()
        self.updateStatSetting()
        
        #print sl.getFIELDLIST('mms')
        
        '''
        self.cbFieldValue
        self.chbFilterMap
        self.cbStatField
        self.cbStatValue
        self.chbStatMap
        '''
    @pyqtSignature("")
    def on_btnOpenDialog_clicked(self):
        """
        Slot documentation goes here.
        """
        self.selectFiles()
    
    def selectFiles(self):    
        if self.rbMMS.isChecked():
            fileExt = 'log'
        elif  self.rbNewspaper.isChecked():
            fileExt = 'txt'
        else:
            msg.information(self,  'info',  u'请选择文件类型')
            return None
            
        files = QtGui.QFileDialog.getOpenFileNames(self,
                "打开文件", '',
                "Text Files (*.%s)"%fileExt)
        self.lbFiles.clear()
        self.lbFiles.addItems(files)
        print self.lbFiles
        
         
    def refresh(self):
        """
        Slot documentation goes here.
        """
        #proceed the event-loop to prevent from being freezed up
        QtGui.QApplication.processEvents();        
            
#Filter Setting   
    def updateFilterSetting(self):
        print 'select'
        print self.cbFilterField.count()
        
        if self.cbFilterField.count()  == 0:
            self.cbFilterField.addItems(self.sl.getFIELDLIST(self.getFileType()))
  
       
        self.cbFilterValue.clear()
        if self.chbFilterMap.isChecked():
            self.cbFilterValue.addItems(self.sl.getGROUPLIST(self.getFileType(),   self.cbFilterField.currentText()))
        else:
            self.cbFilterValue.addItems(self.sl.getVALUELIST(self.getFileType(),   self.cbFilterField.currentText()))
         
    
    @pyqtSignature("QString")
    def on_cbFilterField_activated(self, p0):
        """
        Slot documentation goes here.
        """
        self.updateFilterSetting()
        
    @pyqtSignature("")
    def on_chbFilterMap_clicked(self):
        """
        Slot documentation goes here.
        """
        self.updateFilterSetting()
    
    @pyqtSignature("")
    def on_btnAddFilter_clicked(self):
        """
        Slot documentation goes here.
        Add Filter selectitems
        """
   
        self.lbProcessor.addItem('Filter,'  + self.cbFilterField.currentText() + ',' + 
                                         self.cbFilterValue.currentText() + ',' +
                                         str(self.chbFilterMap.isChecked())
                                         )
        
   

    
    @pyqtSignature("QModelIndex")
    def on_lbProcessor_doubleClicked(self, index):
        """
        Slot documentation goes here.
        """
        self.lbProcessor.takeItem(self.lbProcessor.currentRow())
        
#Statist Setting
    def updateStatSetting(self):
        if self.cbStatField.count()  == 0:
            self.cbStatField.addItems(self.sl.getFIELDLIST(self.getFileType()))
        
        self.cbStatValue.clear()
        if self.chbStatMap.isChecked():
            #self.cbStatValue.addItems(self.sl.getGROUPLIST(self.getFileType(),   self.cbStatField.currentText()))
            self.cbStatValue.addItems(self.sl.getGROUPLIST(self.getFileType(),   self.cbStatField.currentText()))
        else:
            self.cbStatValue.addItems(self.sl.getVALUELIST(self.getFileType(),   self.cbStatField.currentText()))
        
        if self.cbStatRoutine.count() == 0:
            self.cbStatRoutine.addItems(['standard'])
            
            
    @pyqtSignature("QString")
    def on_cbStatField_activated(self, p0):
        """
        Slot documentation goes here.
        """
      
        self.updateStatSetting()

    
    @pyqtSignature("")
    def on_chbStatMap_clicked(self):
        """
        Slot documentation goes here.
        """
        self.updateStatSetting()
        
    @pyqtSignature("")    
    def on_btnAddStat_clicked(self):
        """
        Slot documentation goes here.
        """
        self.lbProcessor.addItem('Statist,' + self.cbStatField.currentText() + ',' + 
                                            self.cbStatValue.currentText() + ',' + 
                                            str(self.chbStatMap.isChecked()) + ',' +
                                            self.cbStatRoutine.currentText()
                                        )
        
    
    def CreateTaskConfig(self):

        testConfig = {'reader':{'type':'newspaper', 'files':[r'f:\detail_hunan_20110430.txt']},                    
                             'filter':[ {'field':'RECVER', 'value':u'岳阳总', 'flag':True}],     #{'field':'CODE', 'value':u'FAILURE', 'flag':True},             
                             'statist':{'type':'newspaper', 'field':'RECVER', 'value':u'各营业部', 'flag':True, 'out':u'out.xls'},    
                             'view':[{'type':'save', 'file':u'aaa.csv'}]                            
                           }   
                           
        #return testConfig
                   
        
        table = {}        
        #reader
        files = [ unicode(self.lbFiles.item(i).text()) for i in range(self.lbFiles.count())]
        table.update( {'reader': {'type':self.getFileType(), 'files':files }})   
        
        #Filter, Statist, Reporter
        for i in range(self.lbProcessor.count()):
            item = unicode(self.lbProcessor.item(i).text()).split(',')
            print item
            type = item[0]
            if type == 'Filter':
                f = []
                f.append({'field':item[1] , 'value':item[2],  'flag':True if item[3]=='True' else False })
                table.update( {'filter': f})  
                
            elif type == 'Statist':
                table.update( {'statist': {'type':self.getFileType(),  'field':item[1],  'value':item[2],  'flag': True if item[3]=='True' else False }}) 

            #elif type == 'report': 
            table.update({'view':[ {'type':'save',  'file':unicode(self.edSaveFile.text())}]
                                })
            #we can add {'type':'display',  'outlook':'pyqtTable',  'ptable':self.tbResult} to display the result in a table    
            
        return table
        
        
        
    @pyqtSignature("")
    def on_rdTxt_clicked(self):
        """
        Slot documentation goes here.
        """
        self.lbProcessor.addItem('Reporter,' + self.edSaveFile.text() + '.' +self.rdTxt.text())

    @pyqtSignature("")
    def on_rdXls_clicked(self):
        """
        Slot documentation goes here.
        """
        self.lbProcessor.addItem('Reporter,' +  self.edSaveFile.text() + '.'+ self.rdXls.text())

    @pyqtSignature("")
    def on_rdDisplay_clicked(self):
        """
        Slot documentation goes here.
        """
        self.lbProcessor.addItem('Reporter,' +  'display')
        self.reportType = 'display'
    
    @pyqtSignature("")
    def on_btnProcess_clicked(self):
        """
        Slot documentation goes here.
        """
        file = QtGui.QFileDialog.getSaveFileName(self,
                u"保存文件", '',
                "Excel Files (*.%s)"%'xls')
        self.edSaveFile.setText(file)
        self.edtStatus.append(u'开始执行....')
        self.refresh()
        config = self.CreateTaskConfig()
        trans = Parser.TransactionControl(config)
        r = trans.execute()
        self.edtStatus.append(u'执行完成！')
        resultFile = unicode(self.edSaveFile.text()).replace(r'/',  r'//',  1)
        print resultFile
        self.edtStatus.append(u'统计结果导出到' + u'<a href="%s">%s</a>'%(resultFile,  resultFile)+ '\n')
        self.edtStatus.setOpenExternalLinks(True)


    
