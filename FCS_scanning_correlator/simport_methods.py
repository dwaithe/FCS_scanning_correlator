import struct
from xml.etree import ElementTree as ET
from PyQt4 import QtGui, QtCore
import platform
import warnings
import numpy as np
import tifffile as tif_fn

from scorrelation_objects import scanObject
def Import_tiff(filename,par_obj,win_obj):
    tif = tif_fn.TiffFile(str(filename))
    name = str(filename).split('/')[-1]
    text_1, ok_1 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the line sampling (Hz):')
    text_2, ok_2 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the pixel dwell time (us):')

    if ok_1 and ok_2:
        deltat= 1000/float(text_1)
        #pickle.dump(tif.asarray(), open('extra.p',"wb"))

        scanObject(filename,par_obj,[deltat,float(text_2)],tif.asarray(),0,0);
        win_obj.bleachCorr1 = False
        win_obj.bleachCorr2 = False
        win_obj.label.generateList()
        win_obj.GateScanFileListObj.generateList()
        #par_obj.objectRef[-1].cb.setChecked(True)
def Import_lsm(filename,par_obj,win_obj):
    lsm = tif_fn.TiffFile(str(filename))
    name = str(filename).split('/')[-1]
    text_1, ok_1 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the line sampling (Hz):')
    text_2, ok_2 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the pixel dwell time (us):')

    if ok_1 and ok_2:
        deltat= 1000/float(text_1)
        #pickle.dump(tif.asarray(), open('extra.p',"wb"))
        
        scanObject(filename,par_obj,[deltat,float(text_2)],lsm.asarray(),0,0);
        #par_obj.objectRef[-1].cb.setChecked(True)
        win_obj.DeltatEdit.setText(str(deltat));
        
        win_obj.bleachCorr1 = False
        win_obj.bleachCorr2 = False
        win_obj.label.generateList()
        win_obj.GateScanFileListObj.generateList()
class Import_lif():
    def __init__(self, fname, parObj,win_obj):
    
        #filename = 'Scanning_FCS_TopfluorPE_Atto647N.lif'
        self.parObj = parObj
        self.win_obj = win_obj
        self.fname = fname
        #Read file
        self.f = open(self.fname, 'rb')


        #First four bytes are test value 0x70
        struct.unpack('i', self.f.read(4))[0]
        #Next is length of xml in file
        a = int(struct.unpack('i', self.f.read(4))[0])
        #Test value *
        self.f.read(1)
        #Number of characters in file, have to mutiply by 2 to get bytes
        c = int(struct.unpack('i', self.f.read(4))[0])
        xml='';
        for i in range(0,c*2):
            xml = xml + struct.unpack('c', self.f.read(1))[0]
        root = ET.XML(xml)


        LUTName = [];
        memId = [];
        self.store = {};
        LUTName =[];
        dimInfo =[];
        
        
        for neighbor1 in root.findall(".//Element"):
           for nun in neighbor1.findall("./Memory"):
                if int(nun.attrib['Size']) >0 :
                    ele = neighbor1.find('.//ATLConfocalSettingDefinition');
                    try:
                        if ele.attrib['ScanMode'] =="xt":
                            name = neighbor1.attrib['Name']
                            memId = nun.attrib['MemoryBlockID']
                            size = nun.attrib['Size']
                            dwell_time = ele.attrib['PixelDwellTime']
                            dimInfo =[];
                            LUTName =[];
                            bytesInc =[]
                            
                            for nun1 in neighbor1.findall('.//ChannelDescription'):
                                LUTName.append(nun1.attrib['LUTName']);
                                
                            for ele in neighbor1.findall('.//DimensionDescription'):
                                dimInfo.append(ele.attrib['NumberOfElements']);
                                
                                bytesInc.append(ele.attrib['BytesInc']);
                                

                            ele =  neighbor1.find('.//ATLConfocalSettingDefinition');
                            lineTime = ele.attrib['LineTime']
                            
                            self.store[name] =[memId,size]
                            self.store[name].append(LUTName)
                            self.store[name].append(dimInfo)
                            self.store[name].append([lineTime])
                            self.store[name].append(int(bytesInc[0]))
                            self.store[name].append(dwell_time)
                            self.store[name].append(name)

                    except:
                        pass
        if self.parObj.gui == 'show':
            self.win_obj.testWin = self.AppForm(self.store,self)
            self.win_obj.testWin.show()
    def import_lif_sing(self,selList):
        self.imDataStore =[];
        self.imDataDesc=[];
        #temp = store[selList[0]]

        #Memory reading happens once.
        while True:
                #Unpacks header for pixel encoding memory.
                try:
                    struct.unpack('i', self.f.read(4))[0]
                except:
                    break;
                struct.unpack('i', self.f.read(4))[0]
                self.f.read(1)

                if platform.system() == 'Darwin':
                    memSize =  struct.unpack('l', self.f.read(8))[0]
                elif platform.system() == 'Windows':
                    memSize =  struct.unpack('l', self.f.read(4))[0]
                    memSize2 =  struct.unpack('l', self.f.read(4))[0]
                else:
                    memSize =  struct.unpack('l', self.f.read(8))[0]

                
                self.f.read(1)
                c = struct.unpack('i', self.f.read(4))[0]
                


                memDesc ='';
                for i in range(0,c*2):
                    memDesc = memDesc + self.f.read(1)
                #print struct.unpack('i', f.read(4))[0]
                

                #Read a memory block of the correct size.
                #imBinData = self.f.read(memSize)
                memDesc = memDesc.translate(None,'\x00')
                #loadImBool = (memDesc in memId )
                loadImBool = False

                #Catch data if it happens to be in array
                for b in range(0, selList.__len__()):
                    temp = self.store[selList[b]]
                    #print memDesc+' '+temp[0]
                    if temp[0] == memDesc:
                       loadImBool = True
                       bytesInc = self.store[selList[b]][5]
                       break

                
                #If memDesc and temp are in list.
                if memSize >0 and loadImBool == True:
                        
                        imData=[]
                        for c in range(0,memSize,bytesInc):
                            if bytesInc == 1:
                                imBinData = self.f.read(1)
                                byteData = struct.unpack('B',imBinData)[0]
                            elif bytesInc ==2:
                                imBinData = self.f.read(2)
                                byteData = struct.unpack('H',imBinData)[0]

                            imData.append(byteData)
                        self.imDataStore.append(imData)
                        self.imDataDesc.append(temp)
                        #print temp
                        #outChannel = np.array(imDataS
                else:
                    self.f.read(memSize)
        s =[]
        self.win_obj.update_correlation_parameters()
        for i in range(self.imDataDesc.__len__()):
                
            s.append(scanObject(self.fname,self.parObj,self.imDataDesc[i],self.imDataStore[i],0,0));
        
        
        if self.parObj.gui == 'show':
            self.win_obj.bleachCorr1 = False
            self.win_obj.bleachCorr2 = False
            #self.win_obj.bleachCorr1_checked = False
            #self.win_obj.bleachCorr2_checked = False
            self.win_obj.label.generateList()
            self.win_obj.GateScanFileListObj.generateList()
            

        
            self.parObj.objectRef[-1].cb.setChecked(True)
            self.parObj.objectRef[-1].plotOn = True
        #self.parObj.plotDataQueueFn()
    class AppForm(QtGui.QMainWindow):
        def __init__(self, fileArray=None,parObj=None):
            QtGui.QMainWindow.__init__(self)
            self.fileArray = fileArray
            self.create_main_frame()
            self.parObj = parObj
            

        def create_main_frame(self):        
            page = QtGui.QWidget()        

            
            self.setWindowTitle("Select Images to Import")
            vbox0 = QtGui.QVBoxLayout()
            hbox1 = QtGui.QHBoxLayout()
            hbox2 = QtGui.QHBoxLayout()
            vbox1 = QtGui.QVBoxLayout()
            
            c =0 
            for name in self.fileArray:
                c = c+1
                exec("subhbox"+str(c)+" = QtGui.QHBoxLayout()");
                exec("self.check"+str(c)+" = QtGui.QCheckBox()");
                
                exec("self.label"+str(c)+" = QtGui.QLabel()");
                exec("self.label"+str(c)+".setText(\""+str(name)+"\")")
                
                exec("subhbox"+str(c)+".addWidget(self.check"+str(c)+")");
                exec("subhbox"+str(c)+".addWidget(self.label"+str(c)+")");
                exec("subhbox"+str(c)+".addStretch(1)");
                exec("vbox1.addLayout(subhbox"+str(c)+")");
                
                
            self.button = QtGui.QPushButton('load Images')
            hbox1.addLayout(vbox1)
            
            vbox0.addLayout(hbox1)
            vbox0.addLayout(hbox2)
            hbox2.addWidget(self.button)
            page.setLayout(vbox0)
            self.setCentralWidget(page)

            self.connect(self.button, QtCore.SIGNAL("clicked()"), self.clicked)

        def clicked(self):
            
            c=0
            selList =[];
            for name in self.fileArray:
                c = c+1
               
                exec("boolV = self.check"+str(c)+".isChecked()");
                if boolV == True:
                    selList.append(name)
            print selList.__len__()
            self.parObj.import_lif_sing(selList)
            self.close()

        #QtGui.QMessageBox.about(self, "My message box", "Text1 = %s, Text2 = %s" % (self.edit1.text(), self.edit2.text()))
    



"""
class tiff_handler:
    def __init__(self,fname):
        '''fname is the full path '''
        self.im  = PIL.Image.open(fname)

        self.im.seek(0)
        # get image dimensions from the meta data the order is flipped
        # due to row major v col major ordering in tiffs and numpy
        
        self.im_sz = [self.im.tag[0x101][0], self.im.tag[0x100][0],self.im.tag[0x102].__len__()]
        self.cur = self.im.tell()
        num = 0
        while True:
            num = num+1
            try:
                self.im.seek(num)
            except EOFError:
                return None

            self.maxFrames = num


    def get_frame(self,j):
        '''Extracts the jth frame from the image sequence.
        if the frame does not exist return None'''
        try:
            self.im.seek(j)
        except EOFError:
            return None

        self.cur = self.im.tell()
        return np.reshape(self.im.getdata(),self.im_sz)
    def __iter__(self):
        self.im.seek(0)
        self.old = self.cur
        self.cur = self.im.tell()
        return self

    def next(self):
        try:
            self.im.seek(self.cur)
            self.cur = self.im.tell()+1
        except EOFError:
            self.im.seek(self.old)
            self.cur = self.im.tell()
            raise StopIteration
        return np.reshape(self.im.getdata(),self.im_sz)"""
