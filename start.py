#coding=utf-8
import sip 
from PyQt4 import QtCore, QtGui
import sys
from PyQt4 import QtCore
from UI.MainWindow import MainDialog

import re

if __name__ == "__main__":
#   QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("utf-8"))
#   QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("utf-8"))
#   QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf-8"))
    
    app = QtGui.QApplication(sys.argv)
    myapp = MainDialog()   
    myapp.show()   
    sys.exit(app.exec_())
    

