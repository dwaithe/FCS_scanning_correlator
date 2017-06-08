import struct
from xml.etree import ElementTree as ET
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QDialog 
import warnings
import numpy as np
import tifffile as tif_fn
import zlib
import platform
import time

from scorrelation_objects import scanObject
class dialog_import(QDialog):
		def __init__(self, par_obj,win_obj):
			QDialog.__init__(self)
			self.win_obj = win_obj
			self.par_obj = par_obj
		def create_main_frame(self):
			#Creates window with the data files which need loading.        
			self.main_dialog_win = QDialog(self)     
			self.main_dialog_win.setWindowTitle("Select Images to Import")
			vbox0 = QtGui.QVBoxLayout()
			hbox1 = QtGui.QHBoxLayout()
			hbox2 = QtGui.QHBoxLayout()
			vbox1 = QtGui.QVBoxLayout()
			
			c =0 
			for subindex in self.stack_holder:
				
				if self.stack_holder[subindex]['timeseries'] == True and self.stack_holder[subindex]['size'][1] > 500:
					
					c = c+1
					exec("subhbox"+str(c)+" = QtGui.QHBoxLayout()")
				
					exec("self.main_dialog_win.check"+str(c)+" = QtGui.QCheckBox()");
					
					exec("self.main_dialog_win.label"+str(c)+" = QtGui.QLabel()");
					exec("self.main_dialog_win.label"+str(c)+".setText(\""+str(self.stack_holder[subindex]['name'])+"\")")
					
					exec("subhbox"+str(c)+".addWidget(self.main_dialog_win.check"+str(c)+")");
					exec("subhbox"+str(c)+".addWidget(self.main_dialog_win.label"+str(c)+")");
					exec("subhbox"+str(c)+".addStretch(1)");
					exec("vbox1.addLayout(subhbox"+str(c)+")");
				
				
			self.main_dialog_win.button = QtGui.QPushButton('load Images')
			hbox1.addLayout(vbox1)
			hbox2.addWidget(self.main_dialog_win.button)
			vbox0.addLayout(hbox1)
			vbox0.addLayout(hbox2)
			
			#page.setLayout(vbox0)
			self.main_dialog_win.setLayout(vbox0)

			self.connect(self.main_dialog_win.button, QtCore.SIGNAL("clicked()"), self.submit_options)
			self.main_dialog_win.show()
		def next_index(self, subindex):

				self.stack_ind = self.stack_holder[self.selList[subindex]]
				if self.win_obj.yes_to_all == None:
					
					
					self.create_line_sampling("")
				else: 
					
					self.text_1 = self.win_obj.text_1
					self.text_2 = self.win_obj.text_2
					self.ok_1 = True
					self.ok_2 = True
					self.import_data_fn(self)
		
		def submit_options(self):
				
				c=0
				self.selList =[];
				for subindex in self.stack_holder:
					
					if self.stack_holder[subindex]['timeseries'] == True and self.stack_holder[subindex]['size'][1] > 500:
						c = c+1
						exec("boolV = self.main_dialog_win.check"+str(c)+".isChecked()");
						if boolV == True:
							self.selList.append(subindex)
				
				self.ind = 1
				self.main_dialog_win.close()
				self.next_index(0)
				
				
		def create_line_sampling(self,suggest_line_time):        
			self.line_sampling_win = QDialog(self.win_obj)     
			
			
			self.line_sampling_win.setWindowTitle('File: '+self.stack_ind['title']+' '+self.stack_ind['name'])
			vbox0 = QtGui.QVBoxLayout()
			hbox1 = QtGui.QHBoxLayout()
			hbox2 = QtGui.QHBoxLayout()
			vbox1 = QtGui.QVBoxLayout()
			
			
			self.label = QtGui.QLabel('Enter the line sampling (Hz):')

			self.input_text = QtGui.QLineEdit(str(suggest_line_time))	
			self.cancel = QtGui.QPushButton('Cancel')
			self.ok = QtGui.QPushButton('Ok')
			hbox1.addLayout(vbox1)
			hbox1.addWidget(self.label)
			hbox1.addWidget(self.input_text)
			hbox2.addStretch()
			hbox2.addWidget(self.ok)
			hbox2.addWidget(self.cancel)
			
			vbox0.addLayout(hbox1)
			vbox0.addLayout(hbox2)
			
			
			self.line_sampling_win.setLayout(vbox0)
			self.input_text.setFocus(True)
			
			self.connect(self.cancel, QtCore.SIGNAL("clicked()"), self.cancel1)
			self.connect(self.ok, QtCore.SIGNAL("clicked()"), self.ok_fun_1)
			self.line_sampling_win.show()
		def create_pixel_dwell(self):        
			self.dialog_dwell_win = QDialog(self.win_obj)     
			
			self.dialog_dwell_win.setWindowTitle('File: '+self.stack_ind['title']+' '+self.stack_ind['name'])
			vbox0 = QtGui.QVBoxLayout()
			hbox1 = QtGui.QHBoxLayout()
			hbox2 = QtGui.QHBoxLayout()
			vbox1 = QtGui.QVBoxLayout()
			
			
			self.label = QtGui.QLabel('Enter the pixel dwell time (us):')	
			self.input_text = QtGui.QLineEdit('')	
			self.cancel = QtGui.QPushButton('Cancel')
			self.ok = QtGui.QPushButton('Ok')
			hbox1.addLayout(vbox1)
			hbox1.addWidget(self.label)
			hbox1.addWidget(self.input_text)
			hbox2.addStretch()
			hbox2.addWidget(self.ok)
			hbox2.addWidget(self.cancel)
			
			vbox0.addLayout(hbox1)
			vbox0.addLayout(hbox2)
			
			#page.setLayout(vbox0)
			self.dialog_dwell_win.setLayout(vbox0)
			self.input_text.setFocus(True)
			
			self.win_obj.connect(self.cancel, QtCore.SIGNAL("clicked()"), self.cancel2)
			self.win_obj.connect(self.ok, QtCore.SIGNAL("clicked()"), self.ok_fun_2)
			self.dialog_dwell_win.show()
		def create_use_settings(self):        
			self.use_settings_win = QDialog(self.win_obj)     
			
			self.use_settings_win.setWindowTitle('File: '+self.stack_ind['title']+' '+self.stack_ind['name'])
			vbox0 = QtGui.QVBoxLayout()
			hbox1 = QtGui.QHBoxLayout()
			hbox2 = QtGui.QHBoxLayout()
			vbox1 = QtGui.QVBoxLayout()
			
			
			self.label = QtGui.QLabel('Use parameters for remaining images?')	
			self.input_text = QtGui.QLineEdit('')	
			self.yes = QtGui.QPushButton('Yes')
			self.no = QtGui.QPushButton('No')
			hbox1.addLayout(vbox1)
			hbox1.addWidget(self.label)
			hbox2.addStretch()
			hbox2.addWidget(self.yes)
			hbox2.addWidget(self.no)
			hbox2.addStretch()
			
			vbox0.addLayout(hbox1)
			vbox0.addLayout(hbox2)
			
			#page.setLayout(vbox0)
			self.use_settings_win.setLayout(vbox0)
			self.input_text.setFocus(True)
			
			self.connect(self.no, QtCore.SIGNAL("clicked()"), self.no_use_fn)
			self.connect(self.yes, QtCore.SIGNAL("clicked()"), self.yes_use_fn)
			self.use_settings_win.show()
		def ok_fun_1(self):
			self.text_1 = self.input_text.text()
			self.ok_1 = True
			self.line_sampling_win.close()
			self.create_pixel_dwell()
			
		def cancel1(self):
			self.text_1 = []
			self.ok_1 = False
			self.line_sampling_win.close()
		def ok_fun_2(self):
			self.text_2 = self.input_text.text()
			self.ok_2 = True
			self.dialog_dwell_win.close()
			if self.win_obj.last_in_file == True:
				self.import_data_fn(self)
			else:
				self.create_use_settings()
		
		def cancel2(self):
			self.text_2 = []
			self.ok_2 = False
			self.dialog_dwell_win.close()
		def no_use_fn(self):
			self.win_obj.yes_to_all = None
			self.use_settings_win.close()
			self.import_data_fn(self)
		def yes_use_fn(self):
			#Whether to use settings for subsequent files.
			self.win_obj.yes_to_all = True
			self.win_obj.text_1 = self.text_1
			self.win_obj.text_2 = self.text_2
			self.use_settings_win.close()
			self.import_data_fn(self)
def Import_tiff(filename,par_obj,win_obj):
	
	win_obj.diag = dialog_import(par_obj,win_obj)
	def import_data_fn(self):
		deltat= 1000/float(self.text_1)
		#pickle.dump(tif.asarray(), open('extra.p',"wb"))
		ab = self.tif.asarray().astype(np.float64)
		scanObject(filename,par_obj,[deltat,float(self.text_2)/1000000],ab,0,0);
		win_obj.bleachCorr1 = False
		win_obj.bleachCorr2 = False
		win_obj.label.generateList()
		self.win_obj.image_status_text.showMessage("Correlating carpet: File " +str(self.win_obj.file_import.file_index+1)+' of '+str(self.win_obj.file_import.file_list.__len__()))
		self.win_obj.app.processEvents()
		if win_obj.last_in_list == False:
			print 'moving to next file'
			win_obj.file_import.load_next_file()
		else:
			print 'finished with all files'
			win_obj.file_import.post_initial_import()
	win_obj.diag.import_data_fn = import_data_fn



	tif = tif_fn.TiffFile(str(filename))
	name = str(filename).split('/')[-1]
	win_obj.diag.stack_ind = {}
	win_obj.diag.stack_ind['title'] = name
	win_obj.diag.stack_ind['name'] =""
	win_obj.diag.tif = tif
	#There is only carpet in each file.
	win_obj.last_in_file = False
	if win_obj.last_in_list == True:
		win_obj.last_in_file = True
	
	if win_obj.yes_to_all == None:
					
					
		win_obj.diag.create_line_sampling("")
	else: 
		
		win_obj.diag.text_1 = win_obj.diag.win_obj.text_1
		win_obj.diag.text_2 = win_obj.diag.win_obj.text_2
		win_obj.diag.ok_1 = True
		win_obj.diag.ok_2 = True
		win_obj.diag.import_data_fn(win_obj.diag)

	
		
def Import_lsm(filename,par_obj,win_obj):
	
	win_obj.diag = dialog_import(par_obj,win_obj)
	def import_data_fn(self):
		deltat= 1000/float(self.text_1)
		data_array = tif_fn.imread(str(filename),key=0)
		scanObject(filename,par_obj,[deltat,float(self.text_2)/1000000],data_array,0,0);
		win_obj.bleachCorr1 = False
		win_obj.bleachCorr2 = False
		win_obj.DeltatEdit.setText(str(deltat));
		win_obj.label.generateList()
		
		self.win_obj.image_status_text.showMessage("Correlating carpet: File " +str(self.win_obj.file_import.file_index+1)+' of '+str(self.win_obj.file_import.file_list.__len__()))
		self.win_obj.app.processEvents()

		if win_obj.last_in_list == False:
			print 'moving to next file'
			win_obj.file_import.load_next_file()
		else:
			print 'finished with all files'
			win_obj.file_import.post_initial_import()




	win_obj.diag.import_data_fn = import_data_fn
	#There is only carpet in each file.
	

	lsm = tif_fn.TiffFile(str(filename))

	

	filename.replace('\\', '/')
	
	try:
		for page in lsm:
			
			suggest_line_time = 1.0/float(page.tags['cz_lsm_info'].value[23])#lineTime.
			break;
	except:
		suggest_line_time = "0.0"
	name = str(filename).split('/')[-1]
	
	win_obj.diag.stack_ind = {}
	win_obj.diag.stack_ind['title'] = name
	win_obj.diag.stack_ind['name'] =""
	win_obj.diag.lsm = lsm
	
	win_obj.last_in_file = False
	if win_obj.last_in_list == True:
			win_obj.last_in_file = True
	if win_obj.yes_to_all == None:
					
					
		win_obj.diag.create_line_sampling(suggest_line_time)
	else: 
		
		win_obj.diag.text_1 = win_obj.diag.win_obj.text_1
		win_obj.diag.text_2 = win_obj.diag.win_obj.text_2
		win_obj.diag.ok_1 = True
		win_obj.diag.ok_2 = True
		win_obj.diag.import_data_fn(win_obj.diag)

		#win_obj.GateScanFileListObj.generateList()
def Import_msr(fname, par_obj,win_obj):
	"""Function which handles import of individual msr files. """
	

	filename_not_path = fname.split("/")[-1]
	
	

	f = open(fname, 'rb')
	str_lnk = ""
	for i in range(0,10):
		str_lnk = str_lnk+struct.unpack('c', f.read(1))[0]
	
	struct.unpack('I', f.read(4))[0]
	start_x = struct.unpack('Q', f.read(8))[0]
	
	struct.unpack('I', f.read(4))[0]
	z = 0
	stack_holder = {}

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
		
		
		if len_of_desc > 0:
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
		
		stack_holder[z] = stack_details
		z = z+1
		if start_x == 0:
			#print 'end'
			left_over = f.read()

	#Establish whether the imagefile is a time-series. 
	for subindex in stack_holder:
		meta_info =  ET.XML(stack_holder[subindex]['meta'])
		stack_holder[subindex]['timeseries'] = False
		for d in meta_info.findall(".//item"):
			if d.text == 'ExpControl T':
				stack_holder[subindex]['timeseries'] = True
				
			
	
	

	win_obj.diag = dialog_import(par_obj,win_obj)
	win_obj.diag.imDataDesc = {}
	win_obj.diag.stack_holder = stack_holder
	win_obj.last_in_file = False


	
	def import_data_fn(self):
		"""Populates the scannning FCS software with the data."""
		self.imDataDesc[7] = self.stack_ind['name']
		self.imDataDesc[6] = float(self.text_2)/1000000
		self.imDataDesc[3] =  self.stack_ind['size']
		self.imDataDesc[4] = [1.0/float(self.text_1)]
		self.imDataDesc[2] = ['Red']
		scanObject(self.stack_ind['title'],self.par_obj,self.imDataDesc,self.stack_ind['image'].astype(np.float64),0,0)
		self.win_obj.bleachCorr1 = False
		self.win_obj.bleachCorr2 = False
		
		self.win_obj.label.generateList()
		self.par_obj.objectRef[-1].cb.setChecked(True)
		self.par_obj.objectRef[-1].plotOn = True
		

		self.win_obj.image_status_text.showMessage("Correlating carpet: "+str(self.ind)+" of "+str(self.selList.__len__())+". File " +str(self.win_obj.file_import.file_index+1)+' of '+str(self.win_obj.file_import.file_list.__len__()))
			
		if self.ind < self.selList.__len__():
			
			
			self.ind = self.ind+1
			if self.ind == self.selList.__len__():
				self.win_obj.last_in_file = True
			self.next_index(self.ind-1)


		else:
			self.win_obj.app.processEvents()
			#Is it the last file in the list
			if self.win_obj.last_in_list == False:
				print 'moving to next file'

				self.win_obj.file_import.load_next_file()
			else:
				print 'finished with all files'
				self.win_obj.file_import.post_initial_import()
	
	
	win_obj.diag.import_data_fn = import_data_fn
	win_obj.diag.create_main_frame()

class Import_lif():
	def __init__(self, fname, parObj,win_obj):
		"""Class which handles the import of lif files"""
		
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

		
		self.win_obj.diag = self.dialog_import_lif(self.meta_array,self,self.win_obj)
		
	
	def import_lif_sing(self,selList):
		"""Loads the individual lif raw data in to the scanning software"""
		
		self.imDataStore =[];
		self.imDataDesc=[];
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
					   self.win_obj.image_status_text.showMessage("Processing carpet: "+str(count_loaded)+" of "+str(selList.__len__())+". From file: "+str(self.win_obj.file_import.file_num+1)+" of "+str(self.win_obj.file_import.file_list.__len__())+".")
			
					   self.win_obj.app.processEvents()
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
		self.parObj.total_sub_files = self.imDataDesc.__len__()
		for i in range(self.imDataDesc.__len__()):
			self.parObj.file_sub = i 
			self.win_obj.image_status_text.showMessage("Correlating carpet: "+str(i+1)+" of "+str(self.imDataDesc.__len__())+". From file: "+str(self.win_obj.file_import.file_num+1)+" of "+str(self.win_obj.file_import.file_list.__len__())+".")
			
			self.win_obj.fit_obj.app.processEvents()
			s.append(scanObject(self.fname,self.parObj,self.imDataDesc[i],self.imDataStore[i],0,0));
		
		self.win_obj.bleachCorr1 = False
		self.win_obj.bleachCorr2 = False
		self.win_obj.label.generateList()
		self.win_obj.image_status_text.showMessage("Data plotted.")
		
	class dialog_import_lif(QDialog):
		def __init__(self, meta_array,parObj,win_obj):
			QDialog.__init__(self)
			self.meta_array = meta_array
			self.parObj = parObj
			self.win_obj = win_obj
			self.create_main_frame()
			
			

		def create_main_frame(self):        
			self.lif_import_win = QtGui.QWidget()        

			
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
			self.lif_import_win.item_list = []
		
			
			c =0 
			
			for idx in self.meta_array:
				name = self.meta_array[idx]['name']
				item = QtGui.QStandardItem(name)
				item.setCheckable(True)
				item.setCheckState(QtCore.Qt.Unchecked)
				self.series_list_model.appendRow(item)
				self.lif_import_win.item_list.append(item)

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
			
			
			self.lif_import_win.setLayout(vbox0)
			self.lif_import_win.resize(500,500)
			self.load_data_btn.clicked.connect(self.load_data_fn)
			self.check_all_btn.clicked.connect(self.check_all_fn)
			self.lif_import_win.show()
		def check_all_fn(self):
			for item in self.lif_import_win.item_list:
				item.setCheckState(QtCore.Qt.Checked)



		def load_data_fn(self):
			self.lif_import_win.close()
			c=0
			self.parObj.selList =[];
			for idx in self.meta_array:
				model_index = self.series_list_model.index(idx, 0)
				checked = self.series_list_model.data(model_index, QtCore.Qt.CheckStateRole) == QtCore.QVariant(QtCore.Qt.Checked)
				#c = c+1
			   
				#exec("boolV = self.check"+str(c)+".isChecked()");
				if checked == True:

					self.parObj.selList.append(idx)
			self.win_obj.image_status_text.showMessage("Loading carpet: File " +str(self.win_obj.file_import.file_index+1)+' of '+str(self.win_obj.file_import.file_list.__len__()))
					   
			self.win_obj.app.processEvents()
			#Is it the last file in the list
			if self.win_obj.last_in_list == False:
				print 'moving to next file'

				self.win_obj.file_import.total_carpets.append(self.parObj.selList.__len__())
				self.win_obj.file_import.load_next_file()
				
				
				
			else:
				print 'finished with all files'
				self.win_obj.file_import.post_initial_import()
				
		   