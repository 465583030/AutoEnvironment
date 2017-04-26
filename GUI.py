# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HMI-V0.3.ui'
#
# Created: Thu Oct 20 21:35:12 2016
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *
import re,hashlib
import os,os.path
import zipfile
import xml.etree.ElementTree as ET
import subprocess
import sqlite3

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setGeometry(150,100,550,580)

        global Gline
        Gline=[i for i in range(18)]
#default,0:transport,1:His,2:Datapath,3:DataVer,4:SDpath,5:MIpath,6:TBpath,7:StaNam,\
#8:Hostname,9:HostLab,10:HostLoc,11:IPcfgfilepath,12:IPCStaNumb,13:Remarks,14:IPCtext,\
#15:SDIPs,16:TBIPs,17:[MIIPs]
        #initial Gline
        for i in range(18):
            if i==0:
                Gline[i]='Subway'
            else:
                Gline[i]=None
        #print(Gline)

        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 530, 500))
        self.tabWidget.setObjectName("tabWidget")

        self.tabWidget.addTab(Page1(),"需求表填写")
        self.tabWidget.setTabToolTip(0, "To Create the RQList")  

        self.tabWidget.addTab(Page2(),"IP设置")
        self.tabWidget.setTabToolTip(1, "To Set Envs IP addresses")  

        self.tabWidget.addTab(Page3(),"历史记录查找")
        self.tabWidget.setTabToolTip(2, "To view History Record")  

        self.tabWidget.addTab(Page4(),"当前环境操作")
        self.tabWidget.setTabToolTip(3, "To close or updata VMHost") 

        self.tabWidget.addTab(Page5(),"已存在IP查看")
        self.tabWidget.setTabToolTip(4, "To view the IP address exist") 

        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 520, 550, 45))

        self.stackedWidget.addWidget(CreateBT())

        self.retranslateUi(Form)        
        self.tabWidget.setCurrentIndex(0)
        Form.setWindowTitle("需求表")
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.show()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "需求表"))


class CreateBT(QWidget):
    def __init__(self,parent=None):
        super(CreateBT, self).__init__(parent) 
        global Gline
        groupBox= QtWidgets.QGroupBox()
        groupBox.setGeometry(QtCore.QRect(0, 0, 120, 30))
 
        self.pushButton_4 = QtWidgets.QPushButton(groupBox)
        self.pushButton_4.setGeometry(QtCore.QRect(420, 0, 100, 23))
        self.pushButton_4.setText('Submit')
        self.pushButton_4.setText( "检测并提交")

        self.pushButton_3 = QtWidgets.QPushButton(groupBox)
        self.pushButton_3.setGeometry(QtCore.QRect(5, 0, 100, 22))
        self.pushButton_3.setText("帮助和说明")
   
        self.DataVersion = QLabel(groupBox)
        self.DataVersion.setFrameStyle(QFrame.Sunken | QFrame.Panel)
        self.DataVersion.setGeometry(QtCore.QRect(125, 5, 280, 16))
        
        self.pushButton_3.clicked.connect(self.helpdoc)
        self.pushButton_4.clicked.connect(self.examing)


        mainLayout = QVBoxLayout()
        mainLayout.addWidget(groupBox)
        self.setLayout(mainLayout)  

    def helpdoc(self):
        print('helpuu')


    def examing(self):
        print('examing')
        filename=Gline[2].split('/')[-1]
        dirfile='C:/Users/StartFZ/Desktop/AutoToSet/Data/'+filename+'.zip'
        self.zip_dir(Gline[2],dirfile)
        Hash=self.md5sum(dirfile) 
        Gline[3]=Hash
        self.DataVersion.setText('DataVersion:'+Hash)
        print('g',Gline)
        tag= ET.Element('RqList')
        dic={"Env":"Env"}
        Env =ET.SubElement(tag,"Env",{"type":"Station","transport":Gline[0]})
        His2 =ET.SubElement(Env,"History")
        His2.text=Gline[1]
        Data =ET.SubElement(Env,"DataDocument",{"path":Gline[2]})
        Data.text=Gline[3]
        Soft =ET.SubElement(Env,"SoftDocument")
        if Gline[4]!=None:
            Soft.attrib["SDpath"]=Gline[4]
        if Gline[5]!=None:
            Soft.attrib["MIpath"]=Gline[5]
        if Gline[6]!=None:
            Soft.attrib["TBpath"]=Gline[6]
        Hostname2 =ET.SubElement(Env,"Hostname")
        StaN =ET.SubElement(Env,"StationName")
        StaN.text=Gline[7]
        IPC =ET.SubElement(Env,"IPcfg",{"filepath":Gline[11],'StaNumb':Gline[12]})
        if Gline[14]!=None:
            IPC.text=Gline[14]
        if Gline[15]!=None:
            attribSD=Gline[15].split('-')[1]
            IPC.attrib["SDIPs"]=attribSD
        if Gline[16]!=None:
            attribTB=Gline[16].split('-')[1]
            IPC.attrib["TBIPs"]=attribTB
        if Gline[17]!=None:
            for line in Gline[17]:
                attrib=line.split('-')[0]+'-'+line.split('-')[1]
                attribMI=line.split('-')[2]
                IPC.attrib[attrib]=attribMI
        Remarks2=ET.SubElement(Env,"Remarks")
        Remarks2.text=Gline[13]   
        self.CreateXMLfile(Gline[7],'Station',Gline[3],tag)
        
        #caculate the total numb
        numb=0
        if Gline[15]!=None:
            numb+=1
        if Gline[16]!=None:
            numb+=1
        if Gline[17]!=None:
            numb+=len(Gline[17])
        print(numb)
        #invoke the data.exe
        subprocess.Popen('data.exe %s %s'%(Gline[3],numb))






    def CreateXMLfile(self,StationName,Env,Hash,tag):
        if StationName==None:
            StationName='StaName'
        filename='C:/Users/StartFZ/Desktop/RQCollect/'+'temp'+'-'+StationName+'-'+Env+'-'+Hash+'.read.xml'
        file=open(filename,'w',encoding="utf-8")
        file.write(r'''<?xml version="1.0" encoding="utf-8"?>''') 
        file.write("\n") 
        #Generates a string representation of an XML element
        b=ET.tostring(tag,'unicode')
        file.write(b)
        file.close()

    def md5sum(self,fname):
         """ 计算文件的MD5值
         """
         def read_chunks(fh):
             fh.seek(0)
             chunk = fh.read(8096)
             while chunk:
                 yield chunk
                 chunk = fh.read(8096)
             else: #最后要将游标放回文件开头
                 fh.seek(0)
         m = hashlib.md5()
         if isinstance(fname, str) \
                 and os.path.exists(fname):
             #print ('str')
             with open(fname, "rb") as fh:
                 for chunk in read_chunks(fh):
                     m.update(chunk)
         #上传的文件缓存 或 已打开的文件流
         elif fname.__class__.__name__ in ["StringIO", "StringO"] \
                 or isinstance(fname, file):
             for chunk in read_chunks(fname):
                 m.update(chunk)
         else:
             return ""
         return m.hexdigest()

    def zip_dir(self,dirname,zipfilename):
        filelist =[]
        #print('first:',filelist)
        if os.path.isfile(dirname): #为什么不是file呢？
            filelist.append(dirname)
            #print('first:',filelist)
        else:
            for root,dirs,files in os.walk(dirname):
                #print('root',root)
                #print('files',files)
                for name in files:
                    filelist.append(os.path.join(root,name))
                    #print('else:',filelist)
        zf =zipfile.ZipFile(zipfilename,"w", zipfile.zlib.DEFLATED)
        for tar in filelist:  #tar为文件目录
            #print('tar',tar)
            arcname =tar[len(dirname):] #截取定长的子目录，从主目录之后
            #print ('arcname',arcname)
            zf.write(tar,arcname)
        zf.close()


class Page1(QWidget):
    def __init__(self,parent=None):
        super(Page1, self).__init__(parent)
        global Gline 
        self.tab = QtWidgets.QWidget()

        self.stackedWidget = QtWidgets.QStackedWidget(self.tab)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 511, 441))
        self.stackedWidget.setFrameShadow(QtWidgets.QFrame.Raised)
        self.stackedWidget.setObjectName("stackedWidget")
       #$$$$$$$$$$stack1
        self.stackedWidgetPage1 = QtWidgets.QWidget()
        self.stackedWidgetPage1.setObjectName("stackedWidgetPage1")
        self.lineEdit = QtWidgets.QLineEdit(self.stackedWidgetPage1)
        self.lineEdit.setGeometry(QtCore.QRect(150, 20, 271, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.label.setGeometry(QtCore.QRect(40, 20, 81, 16))
        self.label.setObjectName("label")
        self.toolButton = QtWidgets.QToolButton(self.stackedWidgetPage1)
        self.toolButton.setGeometry(QtCore.QRect(450, 20, 37, 18))
        self.toolButton.setObjectName("toolButton")
        self.toolButton_2 = QtWidgets.QToolButton(self.stackedWidgetPage1)
        self.toolButton_2.setGeometry(QtCore.QRect(450, 60, 37, 18))
        self.toolButton_2.setObjectName("toolButton_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.stackedWidgetPage1)
        self.lineEdit_2.setGeometry(QtCore.QRect(150, 60, 271, 20))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_3 = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.label_3.setGeometry(QtCore.QRect(40, 60, 81, 16))
        self.label_3.setObjectName("label_3")
        self.comboBox = QtWidgets.QComboBox(self.stackedWidgetPage1)
        self.comboBox.setGeometry(QtCore.QRect(390, 110, 81, 22))
        self.comboBox.setInputMethodHints(QtCore.Qt.ImhNone)
        self.comboBox.setObjectName("comboBox")
        self.label_2 = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.label_2.setGeometry(QtCore.QRect(290, 120, 54, 12))
        self.label_2.setObjectName("label_2")
        self.label_4 = QtWidgets.QLabel(self.stackedWidgetPage1)
        self.label_4.setGeometry(QtCore.QRect(40, 120, 54, 12))
        self.label_4.setObjectName("label_4")
        self.comboBox_2 = QtWidgets.QComboBox(self.stackedWidgetPage1)
        self.comboBox_2.setGeometry(QtCore.QRect(150, 110, 81, 22))
        self.comboBox_2.setObjectName("comboBox_2")
        #######
        self.stackedWidget.addWidget(self.stackedWidgetPage1)

         #$$$$$$$$$$stack2
        
        self.stackedWidgetPage2 = QtWidgets.QWidget()
        self.stackedWidgetPage2.setObjectName("stackedWidgetPage2")
        self.gridLayout = QtWidgets.QGridLayout(self.stackedWidgetPage2)
        self.gridLayout.setObjectName("gridLayout")


        self.toolButton_5 = QtWidgets.QToolButton(self.stackedWidgetPage2)
        self.toolButton_5.setObjectName("MMI")
        self.toolButton_5.setGeometry(QtCore.QRect(440, 130, 36, 18))
        #self.gridLayout.addWidget(self.toolButton_5, 2, 5, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_8.setObjectName("label_8")
        #self.gridLayout.addWidget(self.label_8, 2, 0, 1, 2)
        self.label_8.setGeometry(QtCore.QRect(9, 135, 95, 16))

        self.toolButton_6 = QtWidgets.QToolButton(self.stackedWidgetPage2)
        self.toolButton_6.setObjectName("CITB")
        #self.gridLayout.addWidget(self.toolButton_6, 3, 5, 1, 1)
        self.toolButton_6.setGeometry(QtCore.QRect(440, 180, 36, 18))
        self.label_6 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_6.setObjectName("label_6")
        #self.gridLayout.addWidget(self.label_6, 1, 0, 1, 2)
        self.label_6.setGeometry(QtCore.QRect(9, 85, 95, 16))

        self.label_10 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_10.setObjectName("label_10")
        #self.gridLayout.addWidget(self.label_10, 4, 0, 1, 2)
        self.label_10.setGeometry(QtCore.QRect(9, 225, 95, 16))

        self.lineEdit_7 = QtWidgets.QLineEdit(self.stackedWidgetPage2)
        self.lineEdit_7.setObjectName("StaNam")
        #self.gridLayout.addWidget(self.lineEdit_7, 4, 2, 1, 1)
        self.lineEdit_7.setGeometry(QtCore.QRect(95, 225, 200, 20))

        self.label_5 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_5.setObjectName("label_5")
        #self.gridLayout.addWidget(self.label_5, 4, 3, 1, 1)
        self.label_5.setGeometry(QtCore.QRect(310, 225, 95, 16))

        self.comboBox_3 = QtWidgets.QComboBox(self.stackedWidgetPage2)
        self.comboBox_3.setObjectName("Transport")
        #self.gridLayout.addWidget(self.comboBox_3, 4, 4, 1, 2)
        self.comboBox_3.addItems(['地铁','大铁'])
        self.comboBox_3.setGeometry(QtCore.QRect(400, 225, 75, 20))


        self.label_11 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_11.setObjectName("label_11")
        #self.gridLayout.addWidget(self.label_11, 5, 0, 1, 1)
        self.label_11.setGeometry(QtCore.QRect(14, 265, 95, 16))
        #self.lineEdit_8 = QtWidgets.QLineEdit(self.stackedWidgetPage2)
        #self.lineEdit_8.setObjectName("lineEdit_8")
        #self.gridLayout.addWidget(self.lineEdit_8, 5, 2, 1, 8)
        #self.gridLayout.setGeometry(QtCore.QRect(440, 130, 36, 18))
        #self.lineEdit_8.setGeometry(QtCore.QRect(95, 272, 330, 60))
        self.Textedit =QtWidgets.QPlainTextEdit(self.stackedWidgetPage2)
        self.Textedit.setGeometry(QtCore.QRect(95, 272, 330, 80))
        self.Textedit.setObjectName('Remarks')
        self.Textedit.setPlainText('运行计划：\n搭建人员：\n联系方式：')
        #print(self.Textedit.toPlainText() )


        self.pushButton = QtWidgets.QPushButton(self.stackedWidgetPage2)
        self.pushButton.setObjectName("pushButton")
        #self.gridLayout.addWidget(self.pushButton, 7, 0, 1, 1)
        self.pushButton.setGeometry(QtCore.QRect(12, 365, 65, 22))
        

        self.label_12 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_12.setObjectName("label_12")
        #self.gridLayout.addWidget(self.label_12, 7, 1, 1, 5)
        self.label_12.setGeometry(QtCore.QRect(100, 365, 395, 16))

        self.pushButton_2 = QtWidgets.QPushButton(self.stackedWidgetPage2)
        self.pushButton_2.setObjectName("pushButton_2")
        #self.gridLayout.addWidget(self.pushButton_2, 8, 0, 1, 1)
        self.pushButton_2.setGeometry(QtCore.QRect(12, 410, 65, 22))

        self.label_13 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_13.setObjectName("label_13")
        #self.gridLayout.addWidget(self.label_13, 8, 1, 1, 5)
        self.label_13.setGeometry(QtCore.QRect(100, 410, 355, 16))

        self.label_9 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_9.setObjectName("label_9")
        #self.gridLayout.addWidget(self.label_9, 3, 0, 1, 2)
        self.label_9.setGeometry(QtCore.QRect(9, 180, 95, 16))

        self.toolButton_3 = QtWidgets.QToolButton(self.stackedWidgetPage2)
        self.toolButton_3.setObjectName("Data")
        #self.gridLayout.addWidget(self.toolButton_3, 0, 5, 1, 1)
        self.toolButton_3.setGeometry(QtCore.QRect(440, 45, 36, 18))

        self.lineEdit_6 = QtWidgets.QLineEdit(self.stackedWidgetPage2)
        self.lineEdit_6.setText("")
        self.lineEdit_6.setObjectName("TBpath")
        #self.gridLayout.addWidget(self.lineEdit_6, 3, 2, 1, 3)
        self.lineEdit_6.setGeometry(QtCore.QRect(95, 180, 330, 20))

        self.lineEdit_3 = QtWidgets.QLineEdit(self.stackedWidgetPage2)
        self.lineEdit_3.setObjectName("Data")
        #self.gridLayout.addWidget(self.lineEdit_3, 0, 2, 1, 3)
        self.lineEdit_3.setGeometry(QtCore.QRect(95, 40, 330, 20))


        self.lineEdit_5 = QtWidgets.QLineEdit(self.stackedWidgetPage2)
        self.lineEdit_5.setText("")
        self.lineEdit_5.setObjectName("MIpath")
        #self.gridLayout.addWidget(self.lineEdit_5, 2, 2, 1, 3)
        self.lineEdit_5.setGeometry(QtCore.QRect(95, 130, 330, 20))

        self.toolButton_4 = QtWidgets.QToolButton(self.stackedWidgetPage2)
        self.toolButton_4.setObjectName("SDM")
        #self.gridLayout.addWidget(self.toolButton_4, 1, 5, 1, 1)
        self.toolButton_4.setGeometry(QtCore.QRect(440, 90, 36, 18))

        self.lineEdit_4 = QtWidgets.QLineEdit(self.stackedWidgetPage2)
        self.lineEdit_4.setText("")
        self.lineEdit_4.setObjectName("SDpath")
        #self.gridLayout.addWidget(self.lineEdit_4, 1, 2, 1, 3)
        self.lineEdit_4.setGeometry(QtCore.QRect(95, 85, 330, 20))

        self.label_7 = QtWidgets.QLabel(self.stackedWidgetPage2)
        self.label_7.setObjectName("label_7")
        #self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.label_7.setGeometry(QtCore.QRect(9, 40, 95, 16))


        self.stackedWidget.addWidget(self.stackedWidgetPage2)



        self.stackedWidget.setCurrentIndex(1)

        self.toolButton_3.clicked.connect(self.filepath)
        self.toolButton_4.clicked.connect(self.filepath)
        self.toolButton_5.clicked.connect(self.filepath)
        self.toolButton_6.clicked.connect(self.filepath)

        #record value
        self.lineEdit_3.textChanged.connect(self.recordvalue)
        self.lineEdit_4.textChanged.connect(self.recordvalue)
        self.lineEdit_5.textChanged.connect(self.recordvalue)
        self.lineEdit_6.textChanged.connect(self.recordvalue)
        self.lineEdit_7.textChanged.connect(self.recordvalue)
        self.Textedit.textChanged.connect(self.recordvalue)
        self.comboBox_3.currentIndexChanged.connect(self.recordvalue)

        self.retranslateUi(self.tab)


        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tab)

        self.setLayout(mainLayout) 

    def recordvalue(self):
        #print(self.sender().objectName())     
        if self.sender().objectName()=='Remarks':
            print(self.sender().toPlainText())
            Gline[13]=self.sender().toPlainText()
        elif self.sender().objectName()=='Transport':
            print(self.sender().currentText())
            Gline[0]=self.sender().currentText()
        elif self.sender().objectName()=='Data':
            Gline[2]=self.sender().text()
        elif self.sender().objectName()=='SDpath':
            Gline[4]=self.sender().text()
        elif self.sender().objectName()=='MIpath':
            Gline[5]=self.sender().text()
        elif self.sender().objectName()=='TBpath':
            Gline[6]=self.sender().text()
        elif self.sender().objectName()=='StaNam':
            Gline[7]=self.sender().text()
        #print(Gline)

    def filepath(self):
        print(self.sender().objectName())
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        if self.sender().objectName()=='Data':
            directory = QFileDialog.getExistingDirectory(self,
                    "QFileDialog-Remarks",
                    r'C:\Users\StartFZ\Desktop\AutoToSet\Data', options=options)
            if directory:
                self.lineEdit_3.setText(directory)
        if self.sender().objectName()=='SDM':
            directory = QFileDialog.getExistingDirectory(self,
                    "QFileDialog-Remarks",
                    r'C:\Users\StartFZ\Desktop\AutoToSet\Soft', options=options)
            if directory:
                self.lineEdit_4.setText(directory)
        if self.sender().objectName()=='MMI':
            directory = QFileDialog.getExistingDirectory(self,
                    "QFileDialog-Remarks",
                    r'C:\Users\StartFZ\Desktop\AutoToSet\Soft', options=options)
            if directory:
                self.lineEdit_5.setText(directory)
        if self.sender().objectName()=='CITB':
            directory = QFileDialog.getExistingDirectory(self,
                    "QFileDialog-Remarks",
                    r'C:\Users\StartFZ\Desktop\AutoToSet\Soft', options=options)
            if directory:
                self.lineEdit_6.setText(directory)      


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.toolButton.setText(_translate("Form", "..."))
        self.toolButton_2.setText(_translate("Form", "..."))
        self.label_3.setText(_translate("Form", "软件文件名称"))
        self.label_2.setText(_translate("Form", "TextLabel"))
        self.label_4.setText(_translate("Form", "TextLabel"))
        self.toolButton_5.setText(_translate("Form", "..."))
        self.label_8.setText(_translate("Form", "MMI文件目录"))
        self.toolButton_6.setText(_translate("Form", "..."))
        self.label_6.setText(_translate("Form", "SDM文件目录"))
        self.label_10.setText(_translate("Form", "站场中文名"))
        self.label_5.setText(_translate("Form", "交通方式"))
        self.label_11.setText(_translate("Form", "备注："))
        self.pushButton.setText(_translate("Form", "列表整合"))
        self.label_12.setText(_translate("Form", "RQlist列表整合：可将同站的多种环境整合为一张列表并载入当前列表"))
        self.pushButton_2.setText(_translate("Form", "列表载入"))
        self.label_13.setText(_translate("Form", "直接载入已填写表单，无整合动作"))
        self.label_9.setText(_translate("Form", "CITB文件目录"))
        self.toolButton_3.setText(_translate("Form", "..."))
        self.toolButton_4.setText(_translate("Form", "..."))
        self.label_7.setText(_translate("Form", "数据文件目录"))

class Page2(QWidget):
    def __init__(self,parent=None):
        super(Page2, self).__init__(parent)

        global Gline

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.ipline=QtWidgets.QLineEdit(self.tab_2)
        self.ipline.setGeometry(QtCore.QRect(15, 12, 420, 20))
        self.ipline.setText('Press < Enter > to get the Default IPcfgFile')

        self.groupBox = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox.setGeometry(QtCore.QRect(140, 50, 230, 100))
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setCheckable(True)
        self.groupBox.setChecked(False)        

        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.label_14 = QtWidgets.QLabel(self.groupBox)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 0, 0, 1, 1)

        self.lineEdit_9 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_9.setObjectName("IP1")
        self.gridLayout_2.addWidget(self.lineEdit_9, 0, 1, 1, 1)

        self.label_15 = QtWidgets.QLabel(self.groupBox)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 1, 0, 1, 1)

        self.lineEdit_10 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_10.setObjectName("IP2")
        self.gridLayout_2.addWidget(self.lineEdit_10, 1, 1, 1, 1)

        self.label_16 = QtWidgets.QLabel(self.groupBox)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 2, 0, 1, 1)

        self.lineEdit_11 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_11.setObjectName("StatNumb")
        self.gridLayout_2.addWidget(self.lineEdit_11, 2, 1, 1, 1)
        #####group2
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 160, 451, 141))
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setChecked(True)        

        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.confirmMi =QtWidgets.QPushButton(self.groupBox_2)
        #self.gridLayout_3.addWidget(self.confirmMi, 0, 3, 1, 1)
        self.confirmMi.setGeometry(QtCore.QRect(360, 5, 75, 26))
        self.confirmMi.setText('确认选择')



        self.checkBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.checkBox.setChecked(True)
        self.checkBox.setTristate(False)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_3.addWidget(self.checkBox, 1, 0, 1, 1)

        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_3.addWidget(self.checkBox_2, 1, 1, 1, 1)

        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout_3.addWidget(self.checkBox_3, 1, 2, 1, 1)

        self.checkBox_4 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout_3.addWidget(self.checkBox_4, 1, 3, 1, 1)

        self.checkBox_8 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_8.setObjectName("checkBox_8")
        self.gridLayout_3.addWidget(self.checkBox_8, 2, 0, 1, 1)

        self.checkBox_7 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_7.setObjectName("checkBox_7")
        self.gridLayout_3.addWidget(self.checkBox_7, 2, 1, 1, 1)

        self.checkBox_6 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_6.setObjectName("checkBox_6")
        self.gridLayout_3.addWidget(self.checkBox_6, 2, 2, 1, 1)

        self.checkBox_5 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_5.setObjectName("checkBox_5")
        self.gridLayout_3.addWidget(self.checkBox_5, 2, 3, 1, 1)
        #group3
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3.setGeometry(QtCore.QRect(9, 326, 451, 121))
        self.groupBox_3.setObjectName("groupBox_3")

        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")

        self.label_18 = QtWidgets.QLabel(self.groupBox_3)
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 3, 0, 1, 1)

        self.lineEdit_14 = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_14.setObjectName("RedPubIP")
        self.gridLayout_4.addWidget(self.lineEdit_14, 3, 1, 1, 1)

        self.label_19 = QtWidgets.QLabel(self.groupBox_3)
        self.label_19.setObjectName("label_19")
        self.gridLayout_4.addWidget(self.label_19, 3, 2, 1, 1)

        self.lineEdit_15 = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_15.setObjectName("RedPriIP")
        self.gridLayout_4.addWidget(self.lineEdit_15, 3, 3, 1, 1)

        self.label_20 = QtWidgets.QLabel(self.groupBox_3)
        self.label_20.setObjectName("label_20")
        self.gridLayout_4.addWidget(self.label_20, 4, 0, 1, 1)

        self.lineEdit_16 = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_16.setObjectName("BluPriIP")
        self.gridLayout_4.addWidget(self.lineEdit_16, 4, 1, 1, 1)

        self.label_21 = QtWidgets.QLabel(self.groupBox_3)
        self.label_21.setObjectName("label_21")
        self.gridLayout_4.addWidget(self.label_21, 4, 2, 1, 1)

        self.lineEdit_17 = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_17.setObjectName("StaNumb")
        self.gridLayout_4.addWidget(self.lineEdit_17, 4, 3, 1, 1)

        self.pushButton_15 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_15.setObjectName("pushButton_15")
        self.pushButton_15.setGeometry(QtCore.QRect(340, 5, 100, 26))

        #self.checkSwitch.stateChanged.connect(self.changeDefault)
        self.pushButton_15.clicked.connect(self.acquireCITBadds)
        self.ipline.returnPressed.connect(self.getIPfile)
        self.ip1=None
        self.ip2=None
        #sdm ip change
        self.lineEdit_9.textChanged.connect(self.recordvalue)
        self.lineEdit_10.textChanged.connect(self.recordvalue)
        self.lineEdit_11.textChanged.connect(self.recordvalue)
        #citb ip change
        self.lineEdit_14.textChanged.connect(self.recordvalue)
        self.lineEdit_15.textChanged.connect(self.recordvalue)
        self.lineEdit_16.textChanged.connect(self.recordvalue)
        self.lineEdit_17.textChanged.connect(self.recordvalue)
        self.checkline=[]
        for i in range(8):
            self.checkline.append(None)
        self.confirmMi.clicked.connect(self.comfirmState)

        self.retranslateUi(self.tab_2)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tab_2)
        self.setLayout(mainLayout)

    def comfirmState(self):
        if self.checkBox.checkState()>0:
            self.checkline[0]='MMIA'
        if self.checkBox_2.checkState()>0:
            self.checkline[1]='MMIB'
        if self.checkBox_3.checkState()>0:
            self.checkline[2]='MMIC'
        if self.checkBox_4.checkState()>0:
            self.checkline[3]='MMID'
        if self.checkBox_5.checkState()>0:
            self.checkline[4]='MMIE'
        if self.checkBox_6.checkState()>0:
            self.checkline[5]='MMIF'
        if self.checkBox_7.checkState()>0:
            self.checkline[6]='MMIG'
        if self.checkBox_8.checkState()>0:
            self.checkline[7]='MMIH'  
        print(self.checkline) 
        listMMI=[]
        MMItext=None
        for t in self.checkline:
            if t!=None:
                if MMItext==None:
                    MMItext=t
                else:
                    MMItext=MMItext+'-'+t
                #print('type',t) #输出为MMIA,MMIB,MMIC
                
                    #搜索定位的关键字
                key='操作'+t[3]+'机'

                (mi1,mi2,mi3) =self.FindIP(Gline[2],'hostcfg.ini',key,'StationID','IPAddr1','IPAddr2')
                miip='MIIPs-'+t+'-'+mi2.split('=')[1].strip(' ').strip('\n')+','+mi3.split('=')[1].strip(' ').strip('\n')
                listMMI.append(miip)
        Gline[12]=mi1.split('=')[1].strip(' ').strip('\n')
        Gline[14]=MMItext
        Gline[17]=listMMI
        #print(Gline)
        self.groupBox_2.setChecked(False) 


    def recordvalue(self):
        #print(self.sender().objectName())
        #print(self.sender().text())
        if self.sender().objectName()=='IP1':
            self.ip1=self.sender().text().strip(' ')
        if self.sender().objectName()=='IP2':
            self.ip2=self.sender().text().strip(' ')
        if self.sender().objectName()=='StatNumb':
            Gline[12]=self.sender().text().strip(' ')
        if self.ip1!=None and self.ip2!=None:
            SDappend='SDIPs-'+self.ip1+','+self.ip2
            Gline[15]=SDappend
        #print('g',Gline)
        if self.sender().objectName()=='RedPubIP' or self.sender().objectName()=='RedPriIP' or self.sender().objectName()=='BluPriIP':
            Gline[16]='TBIPs-'+self.lineEdit_14.text().strip(' ')+','+self.lineEdit_15.text().strip(' ')+','+self.lineEdit_16.text().strip(' ')
            #print(Gline[16])


    def getIPfile(self):
        Ipfile=Gline[2]+'/hostcfg.ini'
        self.ipline.setText(Ipfile)
        Gline[11]=Ipfile
        print(Ipfile)
        if not Gline[4]==None:
            if len(Gline[4].split('/'))>2:
                (sd1,sd2,sd3) =self.FindIP(Gline[2],'hostcfg.ini','系统维护台','StationID','IPAddr1','IPAddr2')
                Gline[12]=sd1.split('=')[1].strip(' ').strip('\n')
                #print(Gline[12])
                SDappend='SDIPs-'+sd2.split('=')[1].strip(' ').strip('\n')+','+sd3.split('=')[1].strip(' ').strip('\n')
                #print(SDappend)
                Gline[15]=SDappend
                print(Gline)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

        self.groupBox.setTitle(_translate("Form", "SDM—手动输入IP和站号"))
        self.label_14.setText(_translate("Form", "IP-1"))
        self.label_15.setText(_translate("Form", "IP-2"))
        self.label_16.setText(_translate("Form", "StatNumb"))
        self.groupBox_2.setTitle(_translate("Form", "MMI-默认IP文件和具体环境选择"))
        self.checkBox.setText(_translate("Form", "MMIA"))
        self.checkBox_2.setText(_translate("Form", "MMIB"))
        self.checkBox_3.setText(_translate("Form", "MMIC"))
        self.checkBox_4.setText(_translate("Form", "MMID"))
        self.checkBox_8.setText(_translate("Form", "MMIE"))
        self.checkBox_7.setText(_translate("Form", "MMIF"))
        self.checkBox_6.setText(_translate("Form", "MMIG"))
        self.checkBox_5.setText(_translate("Form", "MMIH"))
        #self.toolButton_8.setText(_translate("Form", "..."))
        self.groupBox_3.setTitle(_translate("Form", "CITB-默认IP设置"))
        self.label_18.setText(_translate("Form", "RedPubIP"))
        self.label_19.setText(_translate("Form", "RedPriIP"))
        self.label_20.setText(_translate("Form", "BluPriIP"))
        self.label_21.setText(_translate("Form", "StaNumb"))
        self.pushButton_15.setText(_translate("Form", "获取CITB-IPs"))


    def changeDefault(self):
        print(self.stackedWidget_2.currentIndex())
        if self.stackedWidget_2.currentIndex()==0:
            self.stackedWidget_2.setCurrentIndex(1)
            print('change')
        if self.stackedWidget_2.currentIndex()==1:
            self.stackedWidget_2.setCurrentIndex(0)

    def filename(self):
        print(self.sender().objectName())
        if self.sender().objectName()=='MMI':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self,
                    "QFileDialog.getOpenFileName()", self.lineEdit_13.text(),
                    "All Files (*);;Text Files (*.txt)", options=options)
            if fileName:
                self.lineEdit_13.setText(fileName)       
        if self.sender().objectName()=='SDM':
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self,
                    "QFileDialog.getOpenFileName()", self.lineEdit_12.text(),
                    "All Files (*);;Text Files (*.txt)", options=options)
            if fileName:
                self.lineEdit_12.setText(fileName)  

    def acquireCITBadds(self):
        #print('CITB-addrs')
        (s1,s2,s3) =self.FindIP(Gline[2],'hostcfg.ini','系统维护','StationID','IPAddr1','IPAddr2')
        (UpA,DnA)=self.FindcitbIP(Gline[2],'cfg_asdf.ini','userboot.cfg','A')
        (UpB,DnB)=self.FindcitbIP(Gline[2],'cfg_asdf.ini','userboot.cfg','B')
        #print(s1,s2,s3,UpA,DnA,UpB,DnB)
        PubRed=UpA.split('.')[0]+'.'+UpA.split('.')[1]+'.'+UpA.split('.')[2]+'.200'
        PriRed=s2.split('=')[1].split('.')[0].strip()+'.'+s2.split('=')[1].split('.')[1]+'.'+s2.split('=')[1].split('.')[2]+'.200'
        PriBlue=s3.split('=')[1].split('.')[0].strip()+'.'+s3.split('=')[1].split('.')[1]+'.'+s3.split('=')[1].split('.')[2]+'.200'

        self.lineEdit_14.setText(PubRed)
        self.lineEdit_15.setText(PriRed)
        self.lineEdit_16.setText(PriBlue)
        self.lineEdit_17.setText(s1.split('=')[1].strip('').strip('\n'))
        Gline[12]=s1.split('=')[1].strip(' ').strip('\n')
        Gline[16]='TBIPs-'+PubRed+','+PriRed+','+PriBlue


    #search func
    def iterfind(self,path, fnexp):
        for root, dirs, files in os.walk(path):
            for name in files:
                nameLow=name.lower()#将文件名统一转化为小写
                if re.match(fnexp,nameLow):
                    yield os.path.join(root,name)

    def FindIP(self,path,filename,EnvSearch,Search1,Search2,Search3):
        for file in self.iterfind(path,filename):
            #acquire public ;xuRed IP addrs
            (userpath,nam)=os.path.split(file)
            fasdf=open(file)
            context=fasdf.readlines()
            lenth=len(context)-1
            for i in range(lenth):
                if re.search(Search1,context[i]):
                    searc1var=context[i]
                if re.search(Search2,context[i]):
                    searc2var=context[i]        
                if re.search(Search3,context[i]):
                    searc3var=context[i]
                if re.search(EnvSearch,context[i]):
                    return(searc1var,searc2var,searc3var)
                    break
            break

    def FindcitbIP(self,path,filename1,filename2,series):
        userbootpath=None
        for file in self.iterfind(path,filename1):
            #print(file.lower())
            if re.search('down',file.lower()):
                userbootpath=re.sub('down','up',file.lower())
            if re.search('up',file.lower()):
                userbootpath=re.sub('up','down',file.lower())
            #acquire public ;xuRed IP addrs
            #print(file)
            fasdf=open(file)
            context=fasdf.readlines()
            lenth=len(context)-1
            for i in range(lenth):
                if series=='A':
                    if '[ZLC_IPAddr]' in context[i]:
                        if not context[i][0]==';':
                            HostUpM=context[i+1].split('=')[1].split(' ')[1].strip('\n')
                            #print(HostUpM)
                if series=='B':
                    if '[ZLCB_IPAddr]' in context[i]:
                        if not context[i][0]==';':
                            HostUpM=context[i+1].split('=')[1].split(' ')[1].strip('\n')  
                            #print(HostUpM)
        if userbootpath:                     
            (userpath,nam)=os.path.split(userbootpath)
            #print(userpath,nam)
            for file in self.iterfind(userpath,filename2):
                fboot=open(file)
                context=fboot.readlines()
                for line in context:
                    for strr in line.split(' '):
                        #print(strr)
                        if re.search('e=',strr):
                            HostDnM=strr.split('=')[1]   
        else:
            HostUpM='0.0.0.0'
            HostDnM='0.0.0.0'

   
        return(HostUpM,HostDnM)


class Page3(QWidget):
    def __init__(self,parent=None):
        super(Page3, self).__init__(parent)

        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")


        self.listWidget = QtWidgets.QListWidget(self.tab_3)
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 481, 421))
        self.listWidget.setObjectName("listWidget") 
        #sort
        self.listWidget.setSortingEnabled(1)  
        #open file             
        dictionaryFile = QFile('data/History.txt')
        dictionaryFile.open(QIODevice.ReadOnly)
        lines=QTextStream(dictionaryFile).readAll().split() 
        #创建每行内容
        item=[]    
        for word in lines:
            item.append(word)
        #创建列表项
        self.listItem = []
        for lst in item:
            self.listItem.append(QListWidgetItem(QIcon("images/qt.png"),self.tr(lst)))       
        #把列表项添加到listwidget中
        for i in range(len(self.listItem)):
            self.listWidget.insertItem(i+1,self.listItem[i])

        #create search lineEdit
        searchLab=QLabel(self.tab_3)
        searchLab.setGeometry(QtCore.QRect(0, 440, 95, 16))
        searchLab.setText('Search')        
        self.searchLine=QtWidgets.QLineEdit(self.tab_3)
        self.searchLine.setGeometry(QtCore.QRect(100, 440, 405, 26))
        #connect
        self.searchLine.returnPressed.connect(self.search)
        self.listWidget.itemClicked.connect(self.clickitem)      
        #layout
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tab_3)
        self.setLayout(mainLayout) 

    #设置click后变量
    def clickitem(self,obj):
        #print(obj.text())
        message=QMessageBox.question(self,"选择历史记录：",obj.text(),QMessageBox.Yes|QMessageBox.No)        
        if message==QMessageBox.Yes:
            print('yes')
        if message==QMessageBox.No:
            print('No')

    def search(self):
        key=self.sender().text()
        for i in range(len(self.listItem)): 
            if re.search(key,self.listWidget.item(i).text()):
                #print('oooo',self.listWidget.count())
                print(self.listWidget.item(i).text())
                self.searchLine.setText(self.listWidget.item(i).text())
                break       

class Page4(QWidget):
    def __init__(self,parent=None):
        super(Page4, self).__init__(parent)
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")

        self.listWidget = QtWidgets.QListWidget(self.tab_4)
        self.listWidget.setGeometry(QtCore.QRect(5, 5, 260, 441))
        self.listWidget.setObjectName("listWidget") 
        #sort
        self.listWidget.setSortingEnabled(1) 
        dictionaryFile = QFile('data/CurrentEnv.txt')
        dictionaryFile.open(QIODevice.ReadOnly)
        lines=QTextStream(dictionaryFile).readAll().split() 
        #创建每行内容
        self.item=[]    
        for word in lines:
            self.item.append(word)
        #print(self.item)
        #创建列表项
        self.listItem = []
        for lst in self.item:
            lst1=lst.split(',')[0]+','+lst.split(',')[1]+','+lst.split(',')[2]+','+lst.split(',')[3]+','
            self.listItem.append(QListWidgetItem(QIcon("images/cur.png"),self.tr(lst1)))       
        #添加事例项
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item) 
        subtitle = QLabel()
        subtitle.setFrameStyle(QFrame.Sunken | QFrame.Panel)
        subtitle.setText('Hostname,StationNumb,Env,Loction,DataVersion')
        self.listWidget.setItemWidget(item,subtitle)
        #把列表项添加到listwidget中
        for i in range(len(self.listItem)):
            self.listWidget.insertItem(i+1,self.listItem[i])

        self.CreteGroup1()
        self.CreteGroup2()
        self.CreteGroup3()


        self.listWidget.itemClicked.connect(self.clickitem) 


        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tab_4)
        self.setLayout(mainLayout) 

    def clickitem(self,obj):
        #print(obj.text())
        self.VmH.setText(obj.text())
        for lst in self.item:
            if re.search(obj.text().split(',')[0],lst):
                lst2=lst.split(',')[3]+','+lst.split(',')[4]+','
                self.Labc.setText(lst2)



    def CreteGroup1(self):
        #基于self.tab创建groupBox
        groupBox= QtWidgets.QGroupBox(self.tab_4)
        groupBox.setGeometry(QtCore.QRect(270, 0, 220, 190))
        groupBox.setTitle('VMHost_Operator')
        #在gropBox中创建组件，其中坐标为相对位置坐标
        self.VmH=QtWidgets.QLineEdit(groupBox)
        self.VmH.setGeometry(QtCore.QRect(5, 15, 215, 22))
        self.VmH.setObjectName('VMHost')

        Lab =QLabel(groupBox)
        Lab.setGeometry(QtCore.QRect(5, 44, 200, 16))
        Lab.setFrameStyle(QFrame.Sunken | QFrame.Panel)
        Lab.setText('DataVersion:')
        #self.ttext=QtWidgets.QLineEdit(groupBox)
        #self.ttext.setGeometry(QtCore.QRect(80, 44, 120, 22))

        self.progressBar = QtWidgets.QProgressBar(groupBox)
        self.progressBar.setGeometry(QtCore.QRect(5, 80, 205, 22))
        #PerNum=self.getPercent(LabComp)
        self.progressBar.setProperty("value", 20)

        self.pushButton = QtWidgets.QPushButton(groupBox)
        self.pushButton.setGeometry(QtCore.QRect(5, 120, 55, 23))
        self.pushButton.setText('Close')
        Lab2 =QLabel(groupBox)
        Lab2.setGeometry(QtCore.QRect(65, 115, 145, 32))
        Lab2.setText('To close the \n chosen VMHost')       

        self.pushButton2 = QtWidgets.QPushButton(groupBox)
        self.pushButton2.setGeometry(QtCore.QRect(5, 160, 55, 23))
        self.pushButton2.setText('Updata')
        Lab3 =QLabel(groupBox)
        Lab3.setGeometry(QtCore.QRect(65, 155, 145, 32))
        Lab3.setText('To updata the \n whole virtual machine')

        self.VmH.textChanged.connect(self.VMhostChange)
        self.VmH.returnPressed.connect(self.search)
        self.pushButton.clicked.connect(self.toclose)


    def toclose(self):
        #print(self.VmH.text())
        if self.VmH.text():
            VMhost=self.VmH.text().split(',')[0]
            message=QMessageBox.question(self,"关闭操作",'Close the %s ?'%VMhost,QMessageBox.Yes|QMessageBox.No)
            if message==QMessageBox.Yes:
                print('Shutdown the %s'%VMhost)
                conn = sqlite3.connect('data/Database.db')
                c = conn.cursor()
                t=(VMhost,)
                for row in c.execute('SELECT LIP1,LabComp,PartPath FROM DistribInfo WHERE  VMHost=?', t):
                    #print(row)
                    (ClIP,User,partPath)=(row[0],row[1],row[2])
                #ready to close vm
                f=open('../Server/pstools/HIP.txt','w')
                f.write(ClIP+','+User+','+'Username'+','+'Password'+',')
                f.close()
                self.createCtrFile(VMhost,partPath) 
                

                #get history record to History.txt
                fh=open('data/History.txt','a')
                for row in c.execute('SELECT VMHost,StationNumb,Env,Location,LabComp FROM BuildInfo where VMHost=?', t):
                    #print('Cur-Exsit:',row)
                    (VM,St,En,Lo,La)=(row[0],row[1],row[2],row[3],row[4])
                    if St and En:
                        fh.write(VM+','+St+','+En+','+Lo+','+La+','+'\n')
                        #关闭远程的vm
                        subprocess.Popen('..\Server\pstools\shutdnvm.bat')
                        print('Close vm %s suceed'%VMhost)
                fh.close()

                #delete current.txt file context
                f1=open('data/CurrentEnv.txt','r')
                lines =f1.readlines()
                i=0
                for line in lines:
                    #print(i,line)
                    if re.search(VMhost,line):
                        print("delete:",line)
                        lines[i]=''
                    else:
                        lines[i]=line
                        #print("write",line)
                    i+=1
                #print(lines)
                f1.seek(0) 
                f1=open('data/CurrentEnv.txt','w')  
                for line in lines: 
                    f1.write(line)
                f1.close()

                #reload file again to updata
                self.listWidget.clear()
                dictionaryFile = QFile('data/CurrentEnv.txt')
                dictionaryFile.open(QIODevice.ReadOnly)
                lines=QTextStream(dictionaryFile).readAll().split() 
                 #创建每行内容
                self.item=[]    
                for word in lines:
                    self.item.append(word)
                #创建列表项
                self.listItem = []
                for lst in self.item:
                    lst1=lst.split(',')[0]+','+lst.split(',')[1]+','+lst.split(',')[2]+','+lst.split(',')[3]+','
                    self.listItem.append(QListWidgetItem(QIcon("images/cur.png"),self.tr(lst1)))
                #添加事例项
                item = QtWidgets.QListWidgetItem()
                self.listWidget.addItem(item) 
                subtitle = QLabel()
                subtitle.setFrameStyle(QFrame.Sunken | QFrame.Panel)
                subtitle.setText('Hostname,StationNumb,Env,Loction,DataVersion')
                self.listWidget.setItemWidget(item,subtitle)
                #把列表项添加到listwidget中
                for i in range(len(self.listItem)):
                    self.listWidget.insertItem(i+1,self.listItem[i])  

                #updata ii.txt文件,对相应数目进行减一操作
                fi=open('data/ii.txt','r')
                context=fi.readlines()
                tem=int(VMhost[2:5])
                labA='Administrator-C'+str(tem/5+1).split('.')[0]+','
                osTemp=VMhost[0:2]
                i=0
                for row in context:
                    if re.match(labA,row):
                        if re.search('XP',osTemp):
                            context[i]=labA+str(int(row.split(',')[1])-1)+','+row.split(',')[2]+','+row.split(',')[3]
                        if re.search('W7',osTemp):
                            context[i]=labA+row.split(',')[1]+','+str(int(row.split(',')[2])-1)+','+row.split(',')[3]           
                    i+=1
                open('data/ii.txt','w').writelines(context)


                #updata database
                clearlist=['','','','','','','','','','']
                c.execute('UPDATE BuildInfo SET StationNumb=?,DataVersion=?,Env=?,RedPubIP=?,RedPriIP=?,BluPriIP=?,RQList=?,BuildTime=?,Remarks=?,Exist=? where VMHost="'+VMhost+'"',clearlist) 
                conn.commit()
                conn.close()
            if message==QMessageBox.No:
                print('Cancel the Operation')
        else:
            print('Please Chose the Close VM')



    def createCtrFile(self,Hostname,partPath):
        Num=Hostname[2:5]
        Os=Hostname[0:2]
        VM='A'+str(int(Num[2:5])%5)+'-'+Os
        fvmctr=open('../Server/pstools/callstdn.bat','w')
        WHostnametemp='set a="c:/program Files (x86)/VMware/vmware VIX/vmrun.exe"'
        WHostname=WHostnametemp.replace('/','\\')
        WEnvtemp='set b="c:/users/'+partPath+'/Documents/Virtual Machines/'+VM+'/'+VM+'.vmx"'
        WEnv=WEnvtemp.replace('/','\\')
        fvmctr.write(WHostname+'\n'+WEnv+'\n'+'%a% stop %b%')
        fvmctr.close()

    def search(self):
        print(self.sender().objectName())
        listItem = []
        for lst in self.item:
            if self.sender().objectName()=='VMHost':
                if re.search(self.sender().text(),lst):
                    lst3=lst.split(',')[1]+','+lst.split(',')[3]+','+lst.split(',')[5]+','
                    self.VmH.setText(lst3)
        if self.sender().objectName()=='LabComp':
            listItem = []
            self.listWidget3.clear()
            for lst in self.item:
                if re.search(self.sender().text().split(',')[1],lst):
                    lst3=lst.split(',')[3]+','+lst.split(',')[0]+','+lst.split(',')[2]+','
                    listItem.append(QListWidgetItem(QIcon("images/kopeteavailable.png"),self.tr(lst3)))                    
            for i in range(len(listItem)):
                self.listWidget3.insertItem(i+1,listItem[i])           
                
                    

    def VMhostChange(self):
        if len(self.sender().text().split(','))>3:
            self.progressBar.setProperty("value", 5)
            listItem = []
            self.listWidget3.clear()
            for lst in self.item:
                lst1=lst.split(',')[1]+','+lst.split(',')[3]+','+lst.split(',')[5]+','
                if lst.split(',')[3]==self.sender().text().split(',')[1]:
                    listItem.append(QListWidgetItem(QIcon("images/ellipse.png"),self.tr(lst1)))           
            for i in range(len(listItem)):
                self.listWidget3.insertItem(i+1,listItem[i])

    def getPercent(self):
        pass

    def CreteGroup2(self):
        #基于self.tab创建groupBox
        groupBox= QtWidgets.QGroupBox(self.tab_4)
        groupBox.setGeometry(QtCore.QRect(270, 200, 220, 80))
        groupBox.setTitle('LabComp_Operator')

        self.Labc=QtWidgets.QLineEdit(groupBox)
        self.Labc.setGeometry(QtCore.QRect(5, 15, 215, 22))
        self.Labc.setObjectName('LabComp')  

        self.progressBar2 = QtWidgets.QProgressBar(groupBox)
        self.progressBar2.setGeometry(QtCore.QRect(5, 47, 205, 22))
        #PerNum=self.getPercent(LabComp)
        self.progressBar2.setProperty("value", 20)   


        self.Labc.returnPressed.connect(self.search)

    def CreteGroup3(self):
        #基于self.tab创建groupBox
        groupBox= QtWidgets.QGroupBox(self.tab_4)
        groupBox.setGeometry(QtCore.QRect(270, 290, 220, 160))
        groupBox.setTitle('Connect_Env')

        self.listWidget3 = QtWidgets.QListWidget(groupBox)
        self.listWidget3.setGeometry(QtCore.QRect(5, 15, 205, 140))
        self.listWidget3.setObjectName("listWidget") 

        self.listWidget3.itemClicked.connect(self.clickitem3) 

    def clickitem3(self,obj):
        print('yes')
        self.VmH.setText(obj.text())

class Page5(QWidget):
    def __init__(self,parent=None):
        super(Page5, self).__init__(parent)
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")       

        self.listWidget = QtWidgets.QListWidget(self.tab_5)
        self.listWidget.setGeometry(QtCore.QRect(5, 5, 450, 421))
        self.listWidget.setObjectName("listWidget") 
        #sort
        self.listWidget.setSortingEnabled(1) 
        dictionaryFile = QFile('data/History.txt')
        dictionaryFile.open(QIODevice.ReadOnly)
        lines=QTextStream(dictionaryFile).readAll().split() 
        #创建每行内容
        item=[]    
        for word in lines:
            item.append(word)
        #创建列表项
        self.listItem = []
        for lst in item:
            self.listItem.append(QListWidgetItem(QIcon("images/kontact_contacts.png"),self.tr(lst)))       
        #把列表项添加到listwidget中
        for i in range(len(self.listItem)):
            self.listWidget.insertItem(i+1,self.listItem[i])

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.tab_5)
        self.setLayout(mainLayout) 

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = QWidget(None)
    Ui_Form().setupUi(widget)
    sys.exit(app.exec_())
    pass
