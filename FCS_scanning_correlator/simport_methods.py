import struct
from xml.etree import ElementTree as ET
from PyQt4 import QtGui, QtCore
import platform
import warnings
import numpy as np
import tifffile as tif_fn
import zlib

from scorrelation_objects import scanObject
def Import_tiff(filename,par_obj,win_obj):
	tif = tif_fn.TiffFile(str(filename))
	name = str(filename).split('/')[-1]
	text_1, ok_1 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the line sampling (Hz):')
	text_2, ok_2 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the pixel dwell time (us):')

	if ok_1 and ok_2:
		deltat= 1000/float(text_1)
		#pickle.dump(tif.asarray(), open('extra.p',"wb"))

		scanObject(filename,par_obj,[deltat,float(text_2)/1000000],tif.asarray(),0,0);
		win_obj.bleachCorr1 = False
		win_obj.bleachCorr2 = False
		win_obj.label.generateList()
		#win_obj.GateScanFileListObj.generateList()
		
def Import_lsm(filename,par_obj,win_obj):
	lsm = tif_fn.TiffFile(str(filename))
	name = str(filename).split('/')[-1]
	text_1, ok_1 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the line sampling (Hz):')
	text_2, ok_2 = QtGui.QInputDialog.getText(win_obj, 'File: '+name, 'Enter the pixel dwell time (us):')

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
			self.win_obj.testWin.exec_()
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
			#self.win_obj.GateScanFileListObj.generateList()
			

		
			self.parObj.objectRef[-1].cb.setChecked(True)
			self.parObj.objectRef[-1].plotOn = True
		#self.parObj.plotDataQueueFn()
	class AppForm(QtGui.QDialog):
		def __init__(self, fileArray=None,parObj=None):
			QtGui.QDialog.__init__(self)
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
			
			self.setLayout(vbox0)

			self.connect(self.button, QtCore.SIGNAL("clicked()"), self.clicked)

		def clicked(self):
			
			c=0
			selList =[];
			for name in self.fileArray:
				c = c+1
			   
				exec("boolV = self.check"+str(c)+".isChecked()");
				if boolV == True:
					selList.append(name)
		   
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
