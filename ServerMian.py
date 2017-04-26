import zipfile
import os,os.path
import hashlib
import socketserver 
import  threading
import time
from tkinter import *
import shutil
import FunctionDef
import subprocess
import Pmw
import xml.etree.ElementTree as ET
import sqlite3

class MyRequestHandler(socketserver.BaseRequestHandler): 
  def handle(self): 
    print ('...connected from:', self.client_address )
    global TCPdelete
    global ThreadClose
    while True:
       if ThreadClose:
       	 print('TCP-Close')
         sys.exit(0)
         break
       data =self.request.recv(1024).decode()
       if re.search('Startup',data):
       	 print('Start Client-VM %s'%data)
         reply='confirm'
         self.request.send(reply.encode())
         break
       if re.search('errorNo.',data):
         reply='shutdown'
         self.request.send(reply.encode())
         rqlist=data.split(',')[4]
         TCPdelete.append(rqlist)
         print(TCPdelete)
         break
       if re.search('IPaddrs,',data):
         print('Write data:',data)
         f=open('ser/re.txt','a+')
         f.write(data)
         reply='truimph'
         f.write('\n')
         f.close()
         self.request.send(reply.encode())
         break
#TCP线程        
class StartTCP(threading.Thread):
     def __init__(self,remark):
        threading.Thread.__init__(self)
        self.remark =remark        
     def run(self):
        print(self.remark)
        tcpServ = socketserver.ThreadingTCPServer(ADDR, MyRequestHandler) 
        print ('waiting for connection...')
        tcpServ.serve_forever()


#Client-Host startup thread        
class StartCHost(threading.Thread):
    def __init__(self,remark):
        threading.Thread.__init__(self)
        self.remark =remark        
    def run(self): #reload run
        print(self.remark)      
        global TCPinput
        global ThreadClose
        #TCPinput=['W7002-DF-MMIA-5bbf3311d94395b09f9551b9c4408202.read.xml']#,\
        #'W7006-DF-MMIC-5bbf3311d94395b09f9551b9c4408202.read.xml', \
        #'W7007-DF-SDM-5bbf3311d94395b09f9551b9c4408202.read.xml', \
        #'W7012-DF-CITB-5bbf3311d94395b09f9551b9c4408202.read.xml']
        #dict Hostname:(IP,User,partPath)
        while True:
            if ThreadClose:
                sys.exit(0)
                break    
            if TCPinput:
                print('Start VM:',TCPinput[0])
                conn = sqlite3.connect('../HMI/data/Database.db')
                c = conn.cursor()
                Hostname=TCPinput[0].split('-')[0]
                t=(Hostname,)
                for row in c.execute('SELECT LIP1,LabComp,PartPath FROM DistribInfo WHERE  VMHost=?', t):#put ? as a placeholder
                    print(row)
                    (ClIP,User,partPath)=(row[0],row[1],row[2])
                conn.commit()
                conn.close()
                #记录
                f=open('pstools/HIP.txt','w')
                f.write(ClIP+','+User+','+'Username'+','+'Password'+',')
                f.close()
                FunctionDef.createCtrFile(Hostname,partPath) 
                subprocess.Popen(r'pstools\startvm.bat')            
                TCPinput=[]
            else:
                pass
                #print('idle')
            time.sleep(2)
   

#采集界面
class Application(Frame):
  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.pack()
    self.createWidgets()
 
  def createWidgets(self):
    self.hi_there = Button(self,fg="red",bg="black",text="Start\n(click me)",font='courier 20 bold')
    self.hi_there["command"] = self.say_hi
    self.hi_there.pack(side="top")
    #print(self.hi_there.config())
    self.label= Label(self,text='Please Click the button \nwhen you Submit a RQList')
    self.label.pack(side='left')
    self.QUIT = Button(self, text="QUIT",bg="white",command=self.kill)
    self.QUIT.pack(side="bottom")
 #收集用户提交的RQlist，生成Klist表示要处理的RQList
  def say_hi(self):
        print("Read the RQList to acquire new request!")
        global TCPdelete
        global KList
        if len(TCPdelete)>0:
            print(TCPdelete)
            for filename in TCPdelete:
                print('filename',filename)
                clearname=filename.split('.')[0]+'.xml'
                cleardir=os.path.join(r'C:\Users\StartFZ\Desktop\RQCollect',clearname)
                formerdir=os.path.join(r'C:\Users\StartFZ\Desktop\RQCollect',filename)
                os.rename(formerdir,cleardir)
            TCPdelete=[]         
        print('clear',TCPdelete)
        ListRQ=[]
        listRQ=os.listdir(r'C:\Users\StartFZ\Desktop\RQCollect')
        #过滤已read文件
        for filename in listRQ:
            if len(filename.split('-'))>3:
                flistRead=filename.split('.')[1]
                #print(flistRead)
                if not flistRead=='read':
                    ListRQ.append(filename)
        print('RQlist',ListRQ)
        totalNum=len(ListRQ)
        print('TotalNum:',totalNum)
        if totalNum>0:
        #此扫描程序只能检测符合项，重点检测IP冲突，当出问题时将无法搭建此环境
        #1)acquire IPs 
            for Rqlt in ListRQ:
                Rqltdir='C:/Users/StartFZ/Desktop/RQCollect/'+Rqlt
                tree = ET.parse(Rqltdir)
                root = tree.getroot()
                for rq in root.findall('Env'):
                    ty=rq.get('type')
                    hostN=rq.find('Hostname').text
                    AD=rq.find('Hostname').get('LabComp')
                    #收集所有有效信息记录在数据库默认为运行状态，当发生error或关闭时删除记录
                    DataV=rq.find('DataDocument').text
                    timemark =time.strftime('BT:%Y/%m/%d',time.localtime(time.time()))
                    Remarks=rq.find('Remarks').text
                    StaNumb=rq.find('IPcfg').get('StaNumb')
                    if re.search('MMI',ty):
                        atr='MIIPs-'+ty
                        ips=rq.find('IPcfg').get(atr)
                        iplist=(ips.split(',')[0],ips.split(',')[1])
                    if ty=='SDM':
                        ips=rq.find('IPcfg').get('SDIPs')
                        iplist=(ips.split(',')[0],ips.split(',')[1])
                    if ty=='CITB':
                        ips=rq.find('IPcfg').get('TBIPs')
                        iplist=(ips.split(',')[0],ips.split(',')[1],ips.split(',')[2])
                #2）查询IP冲突，若不冲突则记录入数据库中
                conn = sqlite3.connect('../HMI/data/Database.db')
                c = conn.cursor() 
                TestSucess=True
                for tk in iplist:
                    t=(tk,tk,tk)
                    for row in c.execute('SELECT * FROM BuildInfo WHERE RedPriIP=? or BluPriIP=? or RedPubIP=?', t):
                        TestSucess=False

                 ######       
                if TestSucess:
                    #记录IPs入数据库,
                    if len(iplist)>2:
                        c.execute('UPDATE BuildInfo SET RedPubIP=?,RedPriIP=?,BluPriIP=? where VMHost="'+hostN+'"' ,iplist)
                    if len(iplist)<3:
                        c.execute('UPDATE BuildInfo SET RedPriIP=?,BluPriIP=? where VMHost="'+hostN+'"' ,iplist) 
                    #记录其他信息入数据库
                    if re.search('XP',hostN):
                        ex='XP-'+AD.split('-')[1]
                    if re.search('W7',hostN):
                        ex='W7-'+AD.split('-')[1]
                    Re=(StaNumb,DataV,ty,Rqlt,timemark,Remarks,ex)
                    c.execute('UPDATE BuildInfo SET StationNumb=?,DataVersion=?,Env=?,RQList=?,BuildTime=?,Remarks=?,Exist=? where VMHost="'+hostN+'"',Re)                   
                   
                   #更新实验室搭建虚拟机数据ii文件
                    ADList=['Administrator-C1','Administrator-C2','Administrator-C3','Administrator-C4',\
                    'Administrator-C5','Administrator-C6','Administrator-C7','Administrator-C8',\
                    'Administrator-C9','Administrator-C10','Administrator-C11','Administrator-C12',\
                    'Administrator-C13','Administrator-C14','Administrator-C15','Administrator-C16',\
                    'Administrator-C17','Administrator-C18','Administrator-C19','Administrator-C20',\
                    'Administrator-C21','Administrator-C22','Administrator-C23','Administrator-C24']
                    fii=open('../HMI/data/ii.txt','w')
                    for t in ADList:
                        #print('t',t)
                        k=(t,)
                        countXP=0
                        countW7=0
                        for row in c.execute('SELECT Exist FROM BuildInfo WHERE LabComp=?', k):
                            #print('r',row)
                            oo=row[0]
                            if oo:
                                if re.search('XP',oo):
                                    countXP+=1
                                if re.search('W7',oo):
                                    countW7+=1
                        fii.write(t+','+str(countXP)+','+str(countW7)+',per\n')
                    fii.close()
                    #更新当前运行环境记录文件CurrentEnv
                    fcur=open('../HMI/data/CurrentEnv.txt','w')
                    for row in c.execute('SELECT VMHost,StationNumb,Env,Location,LabComp,DataVersion FROM BuildInfo where Exist!="NULL" and Exist!=""'):
                        print('Cur-Exsit:',row)
                        (VM,St,En,Lo,La,Da)=(row[0],row[1],row[2],row[3],row[4],row[5])
                        print(VM)
                        fcur.write(VM+','+St+','+En+','+Lo+','+La+','+Da+','+'\n')
                    fcur.close()
                    conn.commit()
                    conn.close()
                 #在文件无error的情况下，将文件名录入KList，并将名称改为..read.txt
                    newname=Rqlt.split('.')[0]+'.read.'+Rqlt.split('.')[1]
                    #print('ai',newname)
                    newdir=os.path.join(r'C:\Users\StartFZ\Desktop\RQCollect',newname)
                    os.rename(Rqltdir,newdir)
                    KList.append(newname)
                else:
                    conn.commit()
                    conn.close()
                    print('IP Conflict!!!')
        print('Klist',KList)

   #结束所有线程          
  def kill(self):
  	   global  ThreadClose
  	   ThreadClose=True
  	   sys.exit(0)       
#界面开启线程     
class collect(threading.Thread):
    def __init__(self,remark):
        threading.Thread.__init__(self)
        self.remark =remark        
    def run(self): #reload run
        print(self.remark)
        global root#不为global的话在其他class中不识别，且即使这还是不能跨文件定义
        root = Tk() #Main windows of the app
        app = Application()
        # 设置窗口标题:
        app.master.title('Auto-Version0.1.0')
        #设置大小,位置
        root.geometry('260x130+400+200')
        # 主消息循环:
        app.mainloop()
 

#执行线程       
class execute(threading.Thread):
    def __init__(self,remark):
        threading.Thread.__init__(self)
        self.remark =remark        
    def run(self): #reload run
        print(self.remark)
        global ThreadClose
        global KList
        global TCPinput
        #KList=['W7002-DF-MMIA-5bbf3311d94395b09f9551b9c4408202.read.xml',\
        #'W7006-DF-MMIC-5bbf3311d94395b09f9551b9c4408202.read.xml', \
        #'W7007-DF-SDM-5bbf3311d94395b09f9551b9c4408202.read.xml', \
        #'W7012-DF-CITB-5bbf3311d94395b09f9551b9c4408202.read.xml']
        while True:
            time.sleep(5)                   
            print('可执行的列表:',KList)
            if ThreadClose:
              sys.exit(0)
              break
        #获取文件路径，软件版本，HostName，搭建类型，IP配置/站号
            if len(KList)>0:   
                klistcache=KList  
                KList=[]          
                #print(klistcache)
                for filename in klistcache:
                    tree = ET.parse(os.path.join(r'C:\Users\StartFZ\Desktop\RQCollect',filename))
                    root = tree.getroot()
                    for rq in root.findall('Env'):
                        His =rq.find('History').text
                        if  His:
                            print('History Mode')
                            break
                        Transport =rq.get('transport')
                        #print('Transport Type:',Transport)
                        Environment=rq.get('type')
                        ########DataPath
                        Datapath =rq.find('DataDocument').get('path')
                        Dataversion =rq.find('DataDocument').text
                        #change file attrib
                        fdata=open('ser\ChangeAttribute.txt','w')
                        fdata.write(Datapath.strip())
                        fdata.close()
                        subprocess.Popen('ser\ChangeAttribute.bat')
                       #获取文件类型
                        DataType=FunctionDef.FileTypeJudge(Datapath)
                        #print('Dtype',DataType)

                        #########SoftPath
                        if re.search('MMI',Environment):
                            Softwarepath =rq.find('SoftDocument').get('MIpath')
                            at='MIIPs-'+Environment
                            IPls=rq.find('IPcfg').get(at)
                        if re.search('SDM',Environment):
                            Softwarepath =rq.find('SoftDocument').get('SDpath')
                            IPls=rq.find('IPcfg').get('SDIPs')
                        if re.search('CITB',Environment):
                            Softwarepath =rq.find('SoftDocument').get('TBpath')
                            IPls=rq.find('IPcfg').get('TBIPs')
                        #print('SoftPath',Softwarepath)                  
                        SoftType=FunctionDef.FileTypeJudge(Softwarepath)
                        #######服务器path
                        Hostname =rq.find('Hostname').text
                        print('Hostname',Hostname)
                     # 将文件搬运到服务器的共享文件夹,step1:新建文件目录
                        Hostnamedirs=os.path.join(r'C:\Java\apache-tomcat-8.5.4\webapps\ftp6',Hostname)
                        if os.path.exists(Hostnamedirs):
                            shutil.rmtree(Hostnamedirs)
                        os.mkdir(Hostnamedirs)
                     #将文件搬运到服务器的共享文件夹,step2收集完所有必要信息后进行搬运,并计算hash
                        if DataType=='rar':
                            (headD,tailD)=os.path.split(Datapath)
                            #print('tailD',tailD)
                            RarpathD='c:\\'+tailD.split('.')[0]
                            #print(RarpathD)
                            FunctionDef.movefile(RarpathD,Hostnamedirs,DataType,'data',Hostname,Environment)
                        else:
                            FunctionDef.movefile(Datapath,Hostnamedirs,DataType,'data',Hostname,Environment)
                        if SoftType=='rar':
                            (headS,tailS)=os.path.split(Softwarepath)
                            #print('tailS',tailS)
                            RarpathS='c:\\'+tailS.split('.')[0]
                            #print(RarpathS)
                            FunctionDef.movefile(RarpathS,Hostnamedirs,SoftType,'soft',Hostname,Environment)
                        else:
                            FunctionDef.movefile(Softwarepath,Hostnamedirs,SoftType,'soft',Hostname,Environment)
                                                   
                       #将系统配置文件移动到共享文件夹中
                        FunctionDef.moveini(Transport,Environment,Hostnamedirs)
                        #获取IP和StationNumb写入文档Aiptry.ip.txt
                        StaNumb=rq.find('IPcfg').get('StaNumb')
                        fip1=open("ser/Aiptry.ip.txt",'w')
                        if re.search('CITB',Environment):                           
                            IPpri=IPls.split(',')[1]+','+IPls.split(',')[2]
                            IPRpub=IPls.split(',')[0]
                            fip1.write(IPpri+','+StaNumb+','+IPRpub+',')
                            fip1.close()
                        else:
                            fip1.write(IPls+','+StaNumb+',')
                            fip1.close()                 
                       #将iptxt文档移动到共享文件中
                        #shutil.copy('ser/Aiptry.ip.txt',Hostnamedirs)
                        #将RQlist复制到共享文件中
                        shutil.copy(os.path.join(r'C:\Users\StartFZ\Desktop\RQCollect',filename),Hostnamedirs)
                        #生成filelist文档
                        filelist=os.listdir(Hostnamedirs)
                        flist=open(os.path.join(Hostnamedirs,'filelist.list.txt'),'w+')
                        for file in filelist:
                            flist.write(file)
                            flist.write('\n')
                        flist.close()                            
                    TCPinput.append(filename)
                    time.sleep(10)
                    print('TCPinput in 3rd',TCPinput)
                
                     
#Main-Threading to generater Sub-Threading
if __name__ == '__main__':
    global TCPdelete
    TCPdelete =[]
    global TCPinput
    TCPinput =[]
    global KList
    KList=[]
    global ThreadClose
    ThreadClose =False
    #开启服务器通信
    HOST = '' 
    PORT = 21567
    ADDR = (HOST, PORT) 
    t1=StartTCP('The TCP/IP Thread-1')
    t1.start()
    time.sleep(1)
    t2 = collect("The Collect Thread-2")
    t2.start() 
    time.sleep(1)
    t3 = execute("The File-Parse Thread-3")
    t3.start() 
    time.sleep(1)
    t4 = StartCHost("The VM-Control Thread-4")
    t4.start() 
