#coding=utf-8
import unittest
from Parser import TransactionControl, Mapper, TableSet 
class Test(unittest.TestCase):
    def test_TransactionControl(self):
        tconfig = {'reader':{'type':'mms', 'files':[r'F:\log\2011061602.log']},                    
                   'filter':[{'field':u'接收方', 'value':u'岳阳市区', 'flag':True}],               
                   'statist':{'type':'mms', 'field':u'接收方', 'value':u'全选', 'flag':True, 'out':'out.xls'},    
                   'view':[{'type':'save', 'file':'aaa.csv'}]#, {'type':'display', 'outlook':'print'} 
                          #                                                
                   }       
                               
        t = TransactionControl(tconfig)
        #self.assertEqual(t.config['reader'], {'type':'mms', 'files':[r'F:\2011050101.log']})
        t.execute()                                                             