import struct
from xml.etree import ElementTree as ET
from PyQt4 import QtGui, QtCore
import platform
import warnings
import numpy as np
import tifffile as tif_fn
import zlib
import time
import string

from scorrelation_objects import scanObject
def Import_tiff(filename,par_obj,win_obj):
	
	
	tif = tif_fn.TiffFile(str(filename))
	name = str(filename).split('/')[-1]
	reply = None
	if win_obj.yes_to_all == None:
		text_1, ok_1 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the line sampling (Hz):')
		text_2, ok_2 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the pixel dwell time (us):')

		reply = QtGui.QMessageBox.question(win_obj, 'Message', "Use parameters for remaining images?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
	else: 
		text_1 = win_obj.text_1
		text_2 = win_obj.text_2
		ok_1 = True
		ok_2 = True

	if reply == QtGui.QMessageBox.Yes:
		win_obj.yes_to_all = True
		win_obj.text_1 = text_1
		win_obj.text_2 = text_2
	if ok_1 and ok_2:
		
		deltat= 1000/float(text_1)
		#pickle.dump(tif.asarray(), open('extra.p',"wb"))
		ab = tif.asarray()
		scanObject(filename,par_obj,[deltat,float(text_2)/1000000],ab,0,0);
		win_obj.bleachCorr1 = False
		win_obj.bleachCorr2 = False
		win_obj.label.generateList()
		#win_obj.GateScanFileListObj.generateList()
		
def Import_lsm(filename,par_obj,win_obj):
	lsm = tif_fn.TiffFile(str(filename))
	filename.replace('\\', '/')
	name = str(filename).split('/')[-1]
	reply = None
	if win_obj.yes_to_all == None:
		text_1, ok_1 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the line sampling (Hz):')
		text_2, ok_2 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the pixel dwell time (us):')

		reply = QtGui.QMessageBox.question(win_obj, 'Message', "Use parameters for remaining images?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
	else: 
		text_1 = win_obj.text_1
		text_2 = win_obj.text_2
		ok_1 = True
		ok_2 = True

	if reply == QtGui.QMessageBox.Yes:
		win_obj.yes_to_all = True
		win_obj.text_1 = text_1
		win_obj.text_2 = text_2
	
	if ok_1 and ok_2:
		deltat= 1000/float(text_1)
		#pickle.dump(tif.asarray(), open('extra.p',"wb"))
		scanObject(filename,par_obj,[deltat,float(text_2)/1000000],lsm.asarray(),0,0);
		#par_obj.objectRef[-1].cb.setChecked(True)
		win_obj.DeltatEdit.setText(str(deltat));
		
		win_obj.bleachCorr1 = False
		win_obj.bleachCorr2 = False
		win_obj.label.generateList()
		#win_obj.GateScanFileListObj.generateList()
class Import_msr():
	def __init__(self, fname, par_obj,win_obj):
		 #filename = 'Scanning_FCS_TopfluorPE_Atto647N.lif'
		self.par_obj = par_obj
		self.win_obj = win_obj
		self.fname = fname

		filename_not_path = self.fname.split("/")[-1]
		
		

		f = open(fname, 'rb')
		str_lnk = ""
		for i in range(0,10):
			str_lnk = str_lnk+struct.unpack('c', f.read(1))[0]
		
		struct.unpack('I', f.read(4))[0]
		start_x = struct.unpack('Q', f.read(8))[0]
		
		struct.unpack('I', f.read(4))[0]
		z = 0
		self.stack_holder = {}

		while(start_x != 0):
			stack_details = {}
			stack_details['title'] = filename_not_path


			f.seek(start_x)
			str_lnk = ""
			for i in range(0,16):
				str_lnk = str_lnk+struct.unpack('c', f.read(1))[0]
			
			file_version = struct.unpack('I', f.read(4))[0]
			rank = struct.unpack('I', f.read(4))[0] -1
			
			img_size = [0]*rank
			for i in range(0,15):

				if i <rank:
					img_size[i] = struct.unpack('<I', f.read(4))[0]
					#print 'The number of pixels along the axes',img_size[i]
					
				else:
					struct.unpack('<I', f.read(4))[0]
			stack_details['size'] = img_size
			
			for i in range(0,15):
				if i <rank:
					struct.unpack('<d', f.read(8))
				else:
					struct.unpack('<d', f.read(8))[0]
			
			for i in range(0,15):
				if i <rank:
					#print 'The offset: ',
					struct.unpack('<d', f.read(8))
				else:
					struct.unpack('<d', f.read(8))[0]
			dtype = struct.unpack('I', f.read(4))[0]
			exit_state = False
			if dtype != 8:
				#print "I don\'t know what to do with this bit-depth."
				exit_state = True
			
			#print 'dtype: ',dtype
			compression_type = struct.unpack('I', f.read(4))[0]
			compression_level = struct.unpack('I', f.read(4))[0]
			stack_details['compression_type'] = compression_type
			stack_details['compression_level'] = compression_level
			#print 'compression? ', compression_type
			#print 'compression level', compression_level
			len_of_name = struct.unpack('I', f.read(4))[0]
			#print 'name_of_len',len_of_name
			len_of_desc = struct.unpack('I', f.read(4))[0]
			
			#Windows does this a bit differently to other OS :-) always nice.
			if platform.system() == 'Darwin':

				reserved =  struct.unpack('l', f.read(8))[0]
				data_len_disk = struct.unpack('l', f.read(8))[0]
				start_x = struct.unpack('l', f.read(8))[0]
			elif platform.system() == 'Windows':
				reserved =  struct.unpack('l', f.read(4))[0]
				null =  struct.unpack('l', f.read(4))[0]
				data_len_disk =  struct.unpack('l', f.read(4))[0]
				null =  struct.unpack('l', f.read(4))[0]
				start_x =  struct.unpack('l', f.read(4))[0]
				null =  struct.unpack('l', f.read(4))[0]
			else:
				reserved =  struct.unpack('l', f.read(8))[0]
				data_len_disk = struct.unpack('l', f.read(8))[0]
				start_x = struct.unpack('l', f.read(8))[0]


			
			
			#print 'next_stack_pos',start_x
			if exit_state == True:
				continue
			str_lnk = ""
			for i in range(0,len_of_name):
				str_lnk = str_lnk+struct.unpack('c', f.read(1))[0]
			stack_details['name'] = str_lnk
			#print 'name of file:',str_lnk
			#print 'length of description',len_of_desc
			desc = f.read(len_of_desc)
			
			stack_details['desc'] = desc
			root = ET.XML(desc)
			if dtype ==8:
				bit_length = 2
			image = []
			if compression_type == True:
				imagedec = zlib.decompress(f.read(data_len_disk))
			else:
				#print 'nocompression'
				imagedec = f.read(data_len_disk)
			
			#Unpack either original or decompressed data.
			for i in range(0,img_size[0]*img_size[1]*bit_length,bit_length):
				image.append(struct.unpack('h',imagedec[i:i+bit_length])[0])
			   
			stack_details['image'] = np.array(image).reshape(stack_details['size'][1],stack_details['size'][0]).T
			str_lnk =[]
			
			
			#Footer stuff
			footer = f.tell()
			size_of_foot = struct.unpack('I', f.read(4))[0]
			
			for b in range(0, 15):
				#print 'st: ',
				struct.unpack('I', f.read(4))[0]
			for b in range(0, 15):
				#print 'nn: ',
				struct.unpack('I', f.read(4))[0]
			
			
			metadata_len = struct.unpack('I', f.read(4))[0]
			#print 'metadata_len',metadata_len
			
			
			f.seek(footer+size_of_foot)
			#print 'where is this',f.tell()

			for b in range(0,rank+1):
				length = struct.unpack('<I', f.read(4))[0]

				str_lnk = ""
				for i in range(0,length):
					str_lnk = str_lnk+struct.unpack('c', f.read(1))[0]
			   


			start_e = f.tell()
			stack_details['meta'] =f.read(metadata_len)
			
			self.stack_holder[z] = stack_details
			z = z+1
			if start_x == 0:
				#print 'end'
				left_over = f.read()

		#Establish whether the imagefile is a time-series. 
		for subindex in self.stack_holder:
			meta_info =  ET.XML(self.stack_holder[subindex]['meta'])
			self.stack_holder[subindex]['timeseries'] = False
			for d in meta_info.findall(".//item"):
				if d.text == 'ExpControl T':
					self.stack_holder[subindex]['timeseries'] = True
					
				
					
		if self.par_obj.gui == 'show':
			self.win_obj.testWin = self.AppForm(self)
			#self.win_obj.testWin.setWindowModality(QtCore.Qt.ApplicationModal)
			self.win_obj.testWin.exec_()
		
	def import_msr_sing(self, selList):
		
		s = []
		for subindex in selList:
			self.imDataDesc = {}
			text_1, ok_1 = QtGui.QInputDialog.getText(self.win_obj, 'File: '+self.stack_holder[subindex]['title']+' '+self.stack_holder[subindex]['name'], 'Enter the line sampling (Hz):')
			text_2, ok_2 = QtGui.QInputDialog.getText(self.win_obj, 'File: '+self.stack_holder[subindex]['title']+' '+self.stack_holder[subindex]['name'], 'Enter the pixel dwell time (us):')
			self.imDataDesc[7] = self.stack_holder[subindex]['name']
			self.imDataDesc[6] = float(text_2)/1000000
			self.imDataDesc[3] = self.stack_holder[subindex]['size']
			self.imDataDesc[4] = [1.0/float(text_1)]
			self.imDataDesc[2] = ['Red']
		
		
		
				
			s.append(scanObject(self.fname,self.par_obj,self.imDataDesc,self.stack_holder[subindex]['image'].astype(np.float64),0,0));
		
		
		if self.par_obj.gui == 'show':
			self.win_obj.bleachCorr1 = False
			self.win_obj.bleachCorr2 = False
			#self.win_obj.bleachCorr1_checked = False
			#self.win_obj.bleachCorr2_checked = False
			self.win_obj.label.generateList()
			#self.win_obj.GateScanFileListObj.generateList()
			

		
			self.par_obj.objectRef[-1].cb.setChecked(True)
			self.par_obj.objectRef[-1].plotOn = True

	class AppForm(QtGui.QDialog):
			def __init__(self, parent):
				QtGui.QDialog.__init__(self)
				self.parent = parent
				self.create_main_frame()
				
				

			def create_main_frame(self):        
				page = QtGui.QWidget()        

				
				self.setWindowTitle("Select Images to Import")
				vbox0 = QtGui.QVBoxLayout()
				hbox1 = QtGui.QHBoxLayout()
				hbox2 = QtGui.QHBoxLayout()
				vbox1 = QtGui.QVBoxLayout()
				
				c =0 
				for subindex in self.parent.stack_holder:
					
					if self.parent.stack_holder[subindex]['timeseries'] == True and self.parent.stack_holder[subindex]['size'][1] > 500:
						
						c = c+1
						exec("subhbox"+str(c)+" = QtGui.QHBoxLayout()");
						exec("self.check"+str(c)+" = QtGui.QCheckBox()");
						
						exec("self.label"+str(c)+" = QtGui.QLabel()");
						exec("self.label"+str(c)+".setText(\""+str(self.parent.stack_holder[subindex]['name'])+"\")")
						
						exec("subhbox"+str(c)+".addWidget(self.check"+str(c)+")");
						exec("subhbox"+str(c)+".addWidget(self.label"+str(c)+")");
						exec("subhbox"+str(c)+".addStretch(1)");
						exec("vbox1.addLayout(subhbox"+str(c)+")");
					
					
				self.button = QtGui.QPushButton('load Images')
				hbox1.addLayout(vbox1)
				hbox2.addWidget(self.button)
				vbox0.addLayout(hbox1)
				vbox0.addLayout(hbox2)
				
				#page.setLayout(vbox0)
				self.setLayout(vbox0)

				self.connect(self.button, QtCore.SIGNAL("clicked()"), self.clicked)

			def clicked(self):
				
				c=0
				selList =[];
				for subindex in self.parent.stack_holder:
					
					if self.parent.stack_holder[subindex]['timeseries'] == True and self.parent.stack_holder[subindex]['size'][1] > 500:
						c = c+1
						exec("boolV = self.check"+str(c)+".isChecked()");
						if boolV == True:
							selList.append(subindex)
				
				self.parent.import_msr_sing(selList)
				self.close()


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
		len_meta = int(struct.unpack('i', self.f.read(4))[0])
		xml='';
		meta_raw = self.f.read(len_meta*2)
		for i in range(0,meta_raw.__len__()):
			xml = xml + struct.unpack('c', meta_raw[i])[0]
		root = ET.XML(xml)


		LUTName = [];
		memId = [];
		self.meta_array = {};
		LUTName =[];
		dimInfo =[];
		
		count = 0
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
							
							self.meta_array[count] = {'memid':memId,'lutname':LUTName,'diminfo':dimInfo,'linetime':[lineTime],'bytesinc':int(bytesInc[0]),'dwelltime':dwell_time,'name':name}
							
							
							count = count+1
					except:
						pass

		if self.parObj.gui == 'show':
			self.win_obj.testWin = self.AppForm(self.meta_array,self)
			self.win_obj.testWin.exec_()
	def import_lif_sing(self,selList):
		self.imDataStore =[];
		self.imDataDesc=[];
		#temp = store[selList[0]]
		count_loaded = 0
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
				for b in selList:
					
					
					#print memDesc+' '+temp[0]
					if self.meta_array[b]['memid'] == memDesc:
					   loadImBool = True
					   bytesInc = self.meta_array[b]['bytesinc']
					   
					   count_loaded +=1
					   self.win_obj.image_status_text.showMessage("Loading carpet: "+str(count_loaded)+' of '+str(selList.__len__())+' selected.')
					   self.win_obj.fit_obj.app.processEvents()
					   break

				
				#If memDesc and temp are in list.
				if memSize >0 and loadImBool == True:
						
						#This is where the actual data is read in.
						
						imBinData = self.f.read(memSize)
						if bytesInc == 1:
							imData=[0]*imBinData.__len__()
							for iv in range(0,imBinData.__len__(),1):
								byteData = struct.unpack('B',imBinData[iv:iv+1])[0]
								imData[iv] = byteData
						if bytesInc == 2:
							imData=[0]*(imBinData.__len__()/2)
							
							cc = 0
							for iv in range(0,imBinData.__len__(),2):
								byteData = struct.unpack('H',imBinData[iv:iv+2])[0]
								imData[cc] =byteData
								cc = cc+1
							
						
							
						self.imDataStore.append(imData)
						self.imDataDesc.append(self.meta_array[b])
						
						
				else:
					
					if count_loaded == selList.__len__():
						break;
					footer = self.f.tell()
					self.f.seek(footer+memSize)
		
		s =[]
		self.f.close()
		self.win_obj.update_correlation_parameters()
		for i in range(self.imDataDesc.__len__()):
			self.win_obj.image_status_text.showMessage("Correlating carpet: "+str(i+1)+' of '+str(self.imDataDesc.__len__())+' selected.')
			self.win_obj.fit_obj.app.processEvents()
			s.append(scanObject(self.fname,self.parObj,self.imDataDesc[i],self.imDataStore[i],0,0));
		
		
		if self.parObj.gui == 'show':
			self.win_obj.bleachCorr1 = False
			self.win_obj.bleachCorr2 = False
			#self.win_obj.bleachCorr1_checked = False
			#self.win_obj.bleachCorr2_checked = False
			self.win_obj.label.generateList()
			#self.win_obj.GateScanFileListObj.generateList()
			

		
			
		self.win_obj.image_status_text.showMessage("Data plotted.")
		#self.parObj.plotDataQueueFn()
	class AppForm(QtGui.QDialog):
		def __init__(self, meta_array=None,parObj=None):
			QtGui.QDialog.__init__(self)
			self.meta_array = meta_array
			self.parObj = parObj
			self.create_main_frame()
			
			

		def create_main_frame(self):        
			page = QtGui.QWidget()        

			
			self.setWindowTitle("Select Images to Import from: "+self.parObj.fname.split("/")[-1])
			vbox0 = QtGui.QVBoxLayout()
			hbox1 = QtGui.QHBoxLayout()
			hbox2 = QtGui.QHBoxLayout()
			vbox1 = QtGui.QVBoxLayout()

			self.series_list_view = QtGui.QTreeView()
			self.series_list_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
			self.series_list_model = QtGui.QStandardItemModel()
			self.series_list_view.setModel(self.series_list_model)
			self.series_list_view.setHeaderHidden(True)
			self.item_list = []
		
			
			c =0 
			
			for idx in self.meta_array:
				name = self.meta_array[idx]['name']
				item = QtGui.QStandardItem(name)
				item.setCheckable(True)
				item.setCheckState(QtCore.Qt.Unchecked)
				self.series_list_model.appendRow(item)
				self.item_list.append(item)

				linetime = float(self.meta_array[idx]['linetime'][0])*1000
				item.setChild(0,QtGui.QStandardItem("line time: "+str(np.round(linetime,3))+" ms"))
				item.setChild(1,QtGui.QStandardItem("line time: "+str( np.round(1/linetime*1000,1))+" Hz"))
				item.setChild(2,QtGui.QStandardItem("dwell time: "+str( float(self.meta_array[idx]['dwelltime'])*1000000)+" us"))
				item.setChild(3,QtGui.QStandardItem("dimensions: "+str( self.meta_array[idx]['diminfo'])))
				item.setChild(4,QtGui.QStandardItem("number of channels: "+str( self.meta_array[idx]['lutname'].__len__())))
				
				
			self.load_data_btn = QtGui.QPushButton('load Images')
			self.check_all_btn = QtGui.QPushButton('Check All')
			hbox1.addLayout(vbox1)
			
			vbox0.addWidget(self.series_list_view)
			vbox0.addLayout(hbox2)
			hbox2.addWidget(self.check_all_btn)
			hbox2.addWidget(self.load_data_btn)
			
			
			self.setLayout(vbox0)
			self.resize(500,500)
			self.load_data_btn.clicked.connect(self.load_data_fn)
			self.check_all_btn.clicked.connect(self.check_all_fn)
		def check_all_fn(self):
			for item in self.item_list:
				item.setCheckState(QtCore.Qt.Checked)



		def load_data_fn(self):
			self.close()
			c=0
			self.parObj.selList =[];
			for idx in self.meta_array:
				model_index = self.series_list_model.index(idx, 0)
				checked = self.series_list_model.data(model_index, QtCore.Qt.CheckStateRole) == QtCore.QVariant(QtCore.Qt.Checked)
				#c = c+1
			   
				#exec("boolV = self.check"+str(c)+".isChecked()");
				if checked == True:

					self.parObj.selList.append(idx)

		   
			
			

		#QtGui.QMessageBox.about(self, "My message box", "Text1 = %s, Text2 = %s" % (self.edit1.text(), self.edit2.text()))
	
