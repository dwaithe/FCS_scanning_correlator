from __future__ import division
import numpy as np



import sys,os
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow,QComboBox, QDoubleSpinBox, QAction, QWidget, QLabel,QTreeView,QAbstractItemView, QSplitter, QSpinBox
from PyQt5.QtWidgets import QListView,QHBoxLayout,QPushButton,QTextEdit,QTableWidget,QVBoxLayout,QLineEdit, QCheckBox 
from PyQt5.QtWidgets import QStatusBar, QApplication, QTabWidget, QGroupBox, QFileDialog
from PyQt5.QtGui import QIcon
import matplotlib
#matplotlib.use('Agg') # before import pylab

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec
from matplotlib.widgets import  SpanSelector


import matplotlib.cm as cm

sys.path.append('../../FCS_point/FCS_point_correlator/focuspoint')
from simport_methods import Import_lif, Import_tiff, Import_lsm, Import_msr
from splugin_methods import bleachCorr, cropDataWindow, bleachCorr2, bleachCorr3, SpotSizeCalculation
from scorrelation_objects import scanObject
from focuspoint.correlation_objects import corrObject

from focuspoint.fitting_gui import Form
import os.path
import warnings
import _pickle as pickle
import errno
import tifffile as tif_fn
import json
import copy
import uuid
import datetime
#now = datetime.datetime.now()
#print 'trial version. Please contact: Dominic Waithe (dominic.waithe@imm.ox.ac.uk) for full version.'
#if now.year == 2017 and now.month > 7:
#		print 'Your version of the software has expired. Please return to source for up-to-date version'
  

def intensity2bin(intTrace, winInt):
	intTrace = np.array(intTrace)  
	minDecayTime = 0
	maxDecayTime = intTrace.shape[0]
	
	numBins = np.ceil((maxDecayTime-minDecayTime)/winInt)
	maxDecayTime = numBins*winInt
	numBins = maxDecayTime/winInt

	mybins = np.linspace(minDecayTime,maxDecayTime, numBins+1)
	decayScale = mybins[:-1]+(winInt/2)
	#bins are valued as half their span.
	margin = (winInt/2)
	photonsInBin =[]
	for intv in decayScale:
		photonsInBin.append(np.sum(intTrace[intv-margin:margin+intv]))
		 
	return np.array(photonsInBin).astype(np.float32), decayScale

class FileDialog_2(QFileDialog):
	def __init__(self, parent):
		super(FileDialog_2, self).__init__()
		self.parent = parent
		self.setOption(self.DontUseNativeDialog, True)
		self.setFileMode(self.ExistingFiles)
		self.tree = self.findChild(QTreeView)
		
	
	def done(self, intv, override_list=None):
		#Function gets fired when the dialog is closed. intv1 is positive if a selection is made.
		super(QFileDialog, self).done(intv)

		#This is how we extract the details. for the multiple files.
		inds = self.tree.selectionModel().selectedIndexes()
		files = []
		for i in inds:
			if i.column() == 0:
				files.append(os.path.join(str(self.directory().absolutePath()),str(i.data())))
		#self.selectedFiles = files
		
		self.close()
		
		self.parent.file_list = files
		if override_list != None:
			self.parent.file_list = override_list
		
		self.parent.file_index = -1

		if intv == 1:
			#If not 1 then the dialog was cancelled.
			if self.parent.file_list.__len__() == self.parent.file_index+2:
					self.parent.win_obj.last_in_list = True
			

			self.parent.load_next_file()


		


class FileDialog(QMainWindow):
	def __init__(self, win_obj, par_obj, fit_obj):
		super(FileDialog, self).__init__()
	   
		
		self.initUI()
		self.par_obj = par_obj
		self.fit_obj = fit_obj
		self.win_obj = win_obj
		self.total_carpets = []

		
		
	def initUI(self):      

		self.textEdit = QTextEdit()
		self.setCentralWidget(self.textEdit)
		self.statusBar()

		openFile = QAction(QIcon('open.png'), 'Open', self)
		openFile.setShortcut('Ctrl+O')
		openFile.setStatusTip('Open new File')
		openFile.triggered.connect(self.showDialog)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(openFile)       
		
		self.setGeometry(300, 300, 350, 500)
		self.setWindowTitle('File dialog')
		#self.show()
	


	
	def showDialog(self):
		#Intialise Dialog.
		
		try:
			#Try and read the default location for a file.
			filename = os.path.expanduser('~')+'/FCS_Analysis/configLoad'
			filename.replace('\\', '/')

			f = open(filename, 'r')
			self.loadpath =f.readline()
			f.close() 
		except:
				#If not default will do.
				self.loadpath = os.path.expanduser('~')+'/FCS_Analysis/'

		#Create loop which opens dialog box and allows selection of files.
		self.imLif_Arr = []
		self.win_obj.yes_to_all = None
		self.win_obj.last_in_list = False
		
		
		self.file_dialog = FileDialog_2(self)
		self.file_dialog.setDirectory(str(self.loadpath))
		#self.file_dialog.setOption(QFileDialog.DontUseNativeDialog,on=True)
		self.file_dialog.setNameFilters(["lif msr tif and lsm files (*.lif *.msr *.tif *.tiff *.lsm)", "All Files (*.*)"])
		self.file_dialog.selectNameFilter("lif msr tif and lsm files (*.lif *.msr *.tif *.tiff *.lsm)")
		
		#self.file_list = dialog.open(self, 'Open a data file',self.loadpath, 'lif msr tif and lsm files (*.lif *.msr *.tif *.tiff *.lsm);;All Files (*.*)')
		self.file_dialog.show()
	


		
		"""c = 1
		for filename in file_list:
			if file_list.__len__() == c:
				self.win_obj.last_in_list = True
			print 'ccc',c
			nameAndExt = os.path.basename(str(filename)).split('.')
			fileExt = nameAndExt[-1]
			if fileExt == 'lif':
				imLif = Import_lif(filename,self.par_obj,self.win_obj)
				imLif_Arr.append(imLif)

			if fileExt == 'msr':
				self.imMsr = Import_msr(filename,self.par_obj,self.win_obj)
			if fileExt == 'tif' or fileExt == 'tiff':
				imTif = Import_tiff(filename,self.par_obj,self.win_obj)
				self.par_obj.objectRef[-1].cb.setChecked(True)
			if fileExt == 'lsm':
				imTif = Import_lsm(filename,self.par_obj,self.win_obj)
			c +=1 """
	def load_next_file(self):
			
		#	if self.file_list.__len__() == self.file_index:
		#		self.load_next_file()
			#else:
			#	return;
			self.file_sub = 0
			self.total_sub_files =0 
			self.file_index += 1
			self.filename = self.file_list[self.file_index]
			if self.file_list.__len__() == self.file_index+1:
				self.win_obj.last_in_list = True
			
			nameAndExt = os.path.basename(str(self.filename)).split('.')

			
			self.fileExt = nameAndExt[-1]
			if self.fileExt == 'lif':
				imLif = Import_lif(self.filename,self.par_obj,self.win_obj)
				self.imLif_Arr.append(imLif)

			if self.fileExt == 'msr':
				self.imMsr = Import_msr(self.filename,self.par_obj,self.win_obj)
			if self.fileExt == 'tif' or self.fileExt == 'tiff':
				imTif = Import_tiff(self.filename,self.par_obj,self.win_obj)
				#self.par_obj.objectRef[-1].cb.setChecked(True)
			if self.fileExt == 'lsm':
				imTif = Import_lsm(self.filename,self.par_obj,self.win_obj)
			
			
			

	def post_initial_import(self):
			#self.win_obj.yes_to_all = None
			self.file_num =0
			if self.fileExt == 'lif':
				#We actually import the image file after the list selection to speed the process of selection with multiple files.
				
				for imLif in self.imLif_Arr:
					imLif.import_lif_sing(imLif.selList)
					self.file_num += 1
					
			self.par_obj.objectRef[-1].cb.setChecked(True)
			self.par_obj.objectRef[-1].plotOn = True
			self.win_obj.DeltatEdit.setText(str(self.par_obj.objectRef[-1].deltat));
				
			try:
				self.loadpath = str(QtCore.QFileInfo(self.filename).absolutePath())
				config_path = os.path.expanduser('~')+'/FCS_Analysis/configLoad'
				config_path.replace('\\', '/')

				f = open(config_path, 'w')

				f.write(self.loadpath)
				f.close()

			
				
			except:
				pass
			#Sets the first one to be plotted which triggers plotQueueFn
			self.win_obj.image_status_text.showMessage("Import complete")
			self.win_obj.image_status_text.setStyleSheet("color : blue")
			self.win_obj.app.processEvents()
		
		
			

			
		







	
class Window(QWidget):
	def __init__(self, par_obj, fit_obj):
		super(Window, self).__init__()
		self.fit_obj = fit_obj
		self.par_obj = par_obj
		self.generateWindow()
	

	def generateWindow(self):
		# a figure instance to plot on
		self.figure1 = plt.figure(figsize=(10,6))


		self.clickedS1 = None
		self.clickedS2 = None
		self.clim_low = 0
		self.clim_high = None
		self.carpetDisplay = 0
		self.bleach_corr_on = False
		self.toggle_carpet_state = 0
		
		# this is the Canvas Widget that displays the `figure`
		

		self.canvas1 = FigureCanvas(self.figure1)
		#self.figure1.patch.set_facecolor('white')
		self.canvas1.setStyleSheet("padding-left: 5px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		jar = QVBoxLayout()
		jar.addWidget(self.canvas1)


		self.corr_window = QGroupBox('Correlation carpet and selected correlation profiles')
		self.corr_window_layout = QVBoxLayout()
		self.corr_window.setLayout(self.corr_window_layout)
		
		
		self.corr_window_layout.addLayout(jar)
		self.toolbar1 = NavigationToolbar(self.canvas1, self)

		self.corr_window_layout.addWidget(self.toolbar1)

		

		# this is the Navigation widget
		# it takes the Canvas widget and a parent
		

		self.figure2 = plt.figure()
		self.canvas2 = FigureCanvas(self.figure2)

		self.figure3 = plt.figure()
		self.canvas3 = FigureCanvas(self.figure3)


		
		self.label = scanFileList(self,self.par_obj)
		#The table which shows the details of each correlated file. 
		self.modelTab2 = QTableWidget(self)

		self.carpet_browser = QMainWindow()
		self.carpet_browser.setWindowTitle('File browser window')
		self.carpet_browser.modelTab2 = self.modelTab2
		
		self.carpet_browser.setCentralWidget(self.modelTab2)
		

		self.carpet_browser.modelTab2.setRowCount(0)
		self.carpet_browser.modelTab2.setColumnCount(6)
		self.carpet_browser.modelTab2.setColumnWidth(0,80);
		self.carpet_browser.modelTab2.setColumnWidth(1,140);
		self.carpet_browser.modelTab2.setColumnWidth(2,40);
		self.carpet_browser.modelTab2.setColumnWidth(3,140);
		#self.modelTab2.setColumnWidth(4,100);
		self.carpet_browser.modelTab2.setColumnWidth(4,30);
		self.carpet_browser.modelTab2.setColumnWidth(5,100);
		self.carpet_browser.modelTab2.horizontalHeader().setStretchLastSection(True)
		self.carpet_browser.modelTab2.resize(800,400)
		self.carpet_browser.modelTab2.setHorizontalHeaderLabels((",data name,plot, file name,,file path").split(","))

		self.carpet_browser.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		
		
		#The table which shows the details of the time-gating.
		self.modelTab = QTableWidget(self)
		self.modelTab.setRowCount(0)
		self.modelTab.setColumnCount(7)
		self.modelTab.setColumnWidth(0,20);
		self.modelTab.setColumnWidth(1,30);
		self.modelTab.setColumnWidth(2,20);
		self.modelTab.setColumnWidth(3,30);
		self.modelTab.setColumnWidth(4,90);
		self.modelTab.setColumnWidth(5,100);
		self.modelTab.setColumnWidth(6,20);
		self.modelTab.horizontalHeader().setStretchLastSection(True)
		
		self.modelTab.setMinimumSize(340,200)
		self.modelTab.setHorizontalHeaderLabels((",From: , ,To: ,, , , , ").split(","))

		

		
		correlationBtns =  QVBoxLayout()
		corrTopRow = QHBoxLayout()
		self.corrBotRow = QHBoxLayout()
		self.fileDialog = QFileDialog()
		self.centre_panel = QVBoxLayout()
		self.right_panel = QVBoxLayout()


		#LEFT PANEL
		self.left_overview = QHBoxLayout()
		self.left_panel = QVBoxLayout()
		self.left_panel_top = QVBoxLayout()
		
		
		#Plots of the raw data.
		self.raw_group = QGroupBox('Raw data plots')
		self.figure4 = plt.figure(figsize=(2,4))
		self.canvas4 = FigureCanvas(self.figure4)
		#self.figure4.patch.set_facecolor('white')
		self.figure5 = plt.figure(figsize=(2,4))
		self.canvas5 = FigureCanvas(self.figure5)
		#self.figure5.patch.set_facecolor('white')
		
		self.left_panel.addWidget(self.raw_group)
		self.left_panel.addStretch()
		
		self.left_panel_top.addWidget(self.canvas4)
		self.left_panel_top.addWidget(self.canvas5)
		self.raw_group.setLayout(self.left_panel_top)
		


		#self.toolbar2 = NavigationToolbar(self.canvas4, self)


		#LEFT PANEL btns
		self.left_panel_mid_btns = QHBoxLayout()
		
		self.prev_pane = QPushButton('Prev pane')
		self.prev_pane.setToolTip("Go back one pane in the XT carpet view.")
		self.next_pane = QPushButton('Next pane')
		self.next_pane.setToolTip("Go forward one pane in the XT carpet view.")
		
		self.prev_pane.clicked.connect(self.prev_pane_fn)
		self.next_pane.clicked.connect(self.next_pane_fn)

		#self.left_panel_mid_btns.addWidget(self.toolbar2)
		self.left_panel_mid_btns.addWidget(self.prev_pane)
		self.left_panel_mid_btns.addWidget(self.next_pane)
		self.left_panel_mid_btns.addStretch()
		self.left_panel_top.addLayout(self.left_panel_mid_btns)


		#LEFT PANEL centre
		self.left_panel_centre = QHBoxLayout()
		self.left_panel_centre_right = QVBoxLayout()
		self.left_panel.addLayout(self.left_panel_centre)
		self.left_panel_centre.addWidget(self.modelTab)
		self.left_panel_centre.addLayout(self.left_panel_centre_right)
		self.left_panel_centre.addStretch()
		

		self.left_overview.addLayout(self.left_panel)
		self.left_panel.addStrut(500)
		self.left_overview.addStretch()
		#LEFT PANEL centre right
		self.file_import = FileDialog(self, self.par_obj, self.fit_obj)
		self.openFile = QPushButton('Open File')
		self.openFile.setToolTip("Import an uncorrelated XT timeseries, for processing.")
		self.openFile.clicked.connect(self.file_import.showDialog)
		self.spacer = QLabel()
		main_layout = QHBoxLayout()
		self.crop_data_btn = QPushButton('Crop Carpet')
		self.crop_data_btn.setToolTip('For selecting subsets of pixels for correlation.')
		self.crop_data_win = cropDataWindow(self.par_obj,self)
		self.crop_data_btn.clicked.connect(self.crop_data_win.create_main_frame)
		self.reprocess_btn = QPushButton('reprocess data')
		self.reprocess_btn.setToolTip('Reprocesses data. Run if you change m or Spatial Pixel Binning.')
		self.reprocess_btn.clicked.connect(self.reprocessDataFn)
		
		
		self.mText = QLabel('m (quality):')
		self.mText.resize(50,40)
		self.mEdit =lineEditSp('30',self, self.par_obj)
		self.mEdit.setToolTip('This is represents the number of points to be calculated for each log-level of tau. ')
		self.mEdit.type ='m'


		self.DeltatText = QLabel('Deltat (ms):')
		self.DeltatText.setToolTip('The calculated scanning line time in ms.')
		self.DeltatEdit = QLabel()
		self.DeltatEdit.par_obj = self
		self.DeltatEdit.type = 'deltat'

		self.kcountBinText = QLabel('Photon counting bin: ')
		self.kcountBinText.resize(50,40)
		self.kcountBinEdit = QSpinBox()
		self.kcountBinEdit.setRange(1,10000);
		self.kcountBinEdit.setSingleStep(1)
		self.kcountBinEdit.par_obj = self
		self.kcountBinEdit.resize(40,50)
		

		self.spatialBinText = QLabel()
		self.spatialBinText.setText('Spatial Pixel Binning: ')
		self.spatialBinText.setToolTip('This represents the number of pixels to integrate spatially before correlation.')
		self.spatialBinEdit = QSpinBox()
		self.spatialBinEdit.setRange(1,51);
		self.spatialBinEdit.setSingleStep(2)
		self.spatialBinEdit.par_obj = self
		self.spatialBinEdit.resize(40,50)


		
		self.left_panel_centre_right.addWidget(self.openFile)
		self.left_panel_centre_right.addWidget(self.crop_data_btn)
		self.left_panel_centre_right.addWidget(self.mText)
		self.left_panel_centre_right.addWidget(self.mEdit)
		self.left_panel_centre_right.addWidget(self.DeltatText)
		self.left_panel_centre_right.addWidget(self.DeltatEdit)
		self.left_panel_centre_right.addWidget(self.kcountBinText)
		self.left_panel_centre_right.addWidget(self.kcountBinEdit)
		self.left_panel_centre_right.addWidget(self.spatialBinText)
		self.left_panel_centre_right.addWidget(self.spatialBinEdit)
		self.left_panel_centre_right.addWidget(self.reprocess_btn)
		self.left_panel_centre_right.addStretch()
		self.left_panel_centre_right.setAlignment(QtCore.Qt.AlignTop)

		


		
		self.right_panel.addWidget(self.corr_window)
		self.corr_window_layout.addLayout(correlationBtns)
		
		self.right_panel.addWidget(self.modelTab2)

		self.bleach_corr1_btn = QPushButton('PBC (Fit)')
		self.bleach_corr1_btn.setToolTip("Photobleaching panel for application of mono-exponential function for photobleaching correction.")
		#self.bleachCorr1_btn.setStyleSheet("padding-left: 5px; padding-right: 20px;padding-top: 1px; padding-bottom: 0px;");
		self.bleach_corr_on_off = QPushButton('  OFF  ')
		self.bleach_corr_on_off.setMinimumWidth(80)
		self.bleach_corr_on_off.setStyleSheet(" color: red;");
		self.bleach_corr_on_off.clicked.connect(self.bleachCorr1fn)
		

		self.bleach_corr2_btn = QPushButton('PBC (LA)')
		self.bleach_corr2_btn.setToolTip("Photobleaching panel for application of local averaging correction. ")

		
		self.displayCarpetText = QLabel('Display:')
		self.displayCarpetText.setMinimumHeight(12)
		self.displayCarpetText.setMaximumHeight(18)
		#self.displayCarpetText.setStyleSheet("border-radius:0px;padding-left: 10px; padding-right: 5px;padding-top 5px;");
		self.CH0Auto_btn = QPushButton('Auto CH0')
		self.CH0Auto_btn.setToolTip('Sets software to visualise first channel (CH0)')
		self.CH0Auto_btn.setStyleSheet("color: green;");
		self.CH1Auto_btn = QPushButton('Auto CH1')
		self.CH1Auto_btn.setToolTip('Sets software to visualise second channel (CH1), if available.')
		#self.CH1Auto_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 0px;");
		self.CH01Cross_btn = QPushButton('Cross CH01')
		self.CH01Cross_btn.setToolTip('Sets software to visualise cross-correlation channel (CH01), if available.')

		self.displayExportText = QLabel('Export:')
		self.displayExportText.setMinimumHeight(12)
		self.displayExportText.setMaximumHeight(18)

		#self.displayExportText.setStyleSheet("padding-left: 10px; padding-right: 5px;padding-top: 5px; ");
		self.addRegion_btn = QPushButton('Store Region');
		self.addRegion_btn.setToolTip('Saves the selected Region to the region list.')
		self.clear_region_btn = QPushButton('Clear Region');
		self.clear_region_btn.setToolTip('Clears a region selection, ensuring all pixels will be exported.')
		
		
		
		#Correlation buttons, the top row.
		self.CH0Auto_btn.clicked.connect(self.CH0AutoFn)
		self.CH1Auto_btn.clicked.connect(self.CH1AutoFn)
		self.CH01Cross_btn.clicked.connect(self.CH01CrossFn)
		self.clear_region_btn.clicked.connect(self.clear_region_fn)
		
		self.TGScrollBoxObj = GateScanFileList(self,self.par_obj)
		self.bleach_corr1_plugin = bleachCorr(self.par_obj,self)
		self.bleach_corr2_plugin = bleachCorr2(self.par_obj,self)
		self.bleach_corr1_btn.clicked.connect(self.bleach_corr1_plugin.create_main_frame)
		self.bleach_corr2_btn.clicked.connect(self.bleach_corr2_plugin.create_main_frame)
		self.addRegion_btn.clicked.connect(self.saveRegion)
		
		
		corrTopRow.addWidget(self.bleach_corr1_btn)
		corrTopRow.addWidget(self.bleach_corr2_btn)
		corrTopRow.addWidget(self.bleach_corr_on_off)
		#corrTopRow.addWidget(self.bleachCorr2_on_off)
		corrTopRow.addWidget(self.displayCarpetText)
		corrTopRow.addWidget(self.CH0Auto_btn)
		corrTopRow.addWidget(self.CH1Auto_btn)
		corrTopRow.addWidget(self.CH01Cross_btn)
		corrTopRow.addWidget(self.displayExportText)
		corrTopRow.addWidget(self.addRegion_btn)
		corrTopRow.addWidget(self.clear_region_btn)



		self.folderOutput = folderOutput(self)
		self.folderOutput.type = 'output_corr_dir'

		self.folderSelect_btn = QPushButton('Set Output Folder')
		self.folderSelect_btn.setToolTip('Sets the folder for exporting files to (e.g. CSV files)')
		#self.folderSelect_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)
		
	
		self.save_corr_txt = QLabel('Save:')
		#self.save_corr_txt.setStyleSheet("spacing: 0px;padding-left: 10px; padding-right:2px;padding-top: 0px; padding-bottom: 0px;");
		self.save_corr_txt.setMinimumHeight(12)
		self.save_corr_txt.setMaximumHeight(18)
		self.save_raw_carpet_btn = QPushButton('Raw Intensity to .tiff')
		self.save_raw_carpet_btn.setToolTip('Exports the raw intensity carpet to tiff suitable for subsequent analysis.')
		self.save_corr_carpet_btn = QPushButton('Correlation Carpets to .tiff')
		self.save_corr_carpet_btn.setToolTip('Exports an image of carpet without logarthmic spacing, suitable for subsequent analysis.')
		#self.save_corr_carpet_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.save_corr_carpet_btn.clicked.connect(self.save_carpets)
		self.save_raw_carpet_btn.clicked.connect(self.save_raw_carpet_fn)

		#self.save_log_corr_carpet_btn = QPushButton('Log Norm. Carpet')
		#self.save_log_corr_carpet_btn.setToolTip('Exports an image of correlated carpet with logarthmic spacing')
		#self.save_log_corr_carpet_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		#self.save_log_corr_carpet_btn.clicked.connect(self.save_log_carpets)

		#self.save_figure_btn = QPushButton('Figure')
		#self.save_figure_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		#self.save_figure_btn.clicked.connect(self.save_figure)

		self.spot_size_calc = QPushButton('Calc. Spot Size')

		self.spot_size_calc_plugin = SpotSizeCalculation(self.par_obj,self)
		self.spot_size_calc.clicked.connect(self.spot_size_calc_plugin.create_main_frame)

		

		
		self.corrBotRow.addWidget(self.folderSelect_btn)
		self.corrBotRow.addWidget(self.save_corr_txt )
		self.corrBotRow.addWidget(self.save_raw_carpet_btn)
		self.corrBotRow.addWidget(self.save_corr_carpet_btn)
		#self.corrBotRow.addWidget(self.save_log_corr_carpet_btn)
		#self.corrBotRow.addWidget(self.save_figure_btn)
		#self.corrBotRow.addWidget(self.spot_size_calc)
		self.corrBotRow.addStretch()
		
		
		panel_third_row_btns = QHBoxLayout()
		
		

		self.export_region_btn = QPushButton('Export to Fit');
		self.export_region_btn.setToolTip('Export current carpet to fit interface.')
		self.export_region_btn.clicked.connect(self.export_track_to_fit)
		self.export_all_data_btn = QPushButton('Export All Carpets to Fit')
		self.export_all_data_btn.setToolTip('Exports all carpets in the data viewer to the fitting interface.')
		self.export_all_data_btn.clicked.connect(self.export_all_data_fn)
		self.export_all_data_to_csv_btn = QPushButton('Export All Carpets to CSV')
		self.export_all_data_to_csv_btn.setToolTip('Exports correlated data out of software.')
		self.export_all_data_to_csv_btn.clicked.connect(self.save_all_as_csv_fn)

		self.toggle_carpet_browser_btn = QPushButton('Toggle Carpet Browser')
		self.toggle_carpet_browser_btn.clicked.connect(self.toggle_carpet_browser_fn)
		
		panel_third_row_btns.addWidget(self.export_region_btn)
		panel_third_row_btns.addWidget(self.export_all_data_btn)
		panel_third_row_btns.addWidget(self.export_all_data_to_csv_btn)

		panel_third_row_btns.addStretch()
		panel_third_row_btns.addWidget(self.toggle_carpet_browser_btn)
		
		self.corr_window_layout.setSpacing(4)
		self.corr_window_layout.setContentsMargins(0,0,0,0)
		self.corr_window_layout.addStretch()
		
		self.image_status_text = QStatusBar()
		
		self.image_status_text.showMessage("Please load a data file. ")
		self.image_status_text.setStyleSheet("color : blue")
		self.image_status_text.setFixedWidth(400)
		
		
		self.setLayout(main_layout)
		main_layout.addLayout(self.left_overview)
		
		correlationBtns.addLayout(corrTopRow)
		correlationBtns.addLayout(self.corrBotRow)
		correlationBtns.addLayout(panel_third_row_btns)
		correlationBtns.addStretch()
		main_layout.addLayout(self.right_panel)
		
		
		

		self.left_panel.addWidget(self.image_status_text)
		#Advanced grid structure for the plot windows.
		gs = gridspec.GridSpec(2, 3, height_ratios=[1, 0.98],width_ratios=[0.02, 0.96,0.02]) 
		#Main correlation window
		self.plt1 = self.figure1.add_subplot(gs[0,:])
		

		self.figure1.suptitle('Correlation Function Ouput', fontsize=12)
		#Place holder for the colorbar.
		self.plt6 = self.figure1.add_subplot(gs[1,2:3])
		#The Intensity maxima for each column.
		self.plt3 = self.figure1.add_subplot(gs[1:,0:1])
		#Where the carpet is displayed
		self.plt2 = self.figure1.add_subplot(gs[1,1:2])
		
		#The photon count intensity trace
		self.plt4= self.figure4.add_subplot(111)
		self.figure4.suptitle('Intensity Time Trace', fontsize=12)
		#The XT Trace
		self.plt5= self.figure5.add_subplot(111)
		self.figure5.suptitle('XT Carpet', fontsize=12)

		self.plt1.format_coord = lambda x, y:''
		self.plt2.format_coord = lambda x, y:''
		self.plt3.format_coord = lambda x, y:''
		self.plt4.format_coord = lambda x, y:''
		self.plt5.format_coord = lambda x, y:''
		self.plt6.format_coord = lambda x, y:''
		self.plt1.get_xaxis().set_visible(False)
		self.plt1.get_yaxis().set_visible(False)
		self.plt2.get_xaxis().set_visible(False)
		self.plt2.get_yaxis().set_visible(False)
		self.plt3.get_xaxis().set_visible(False)
		self.plt3.get_yaxis().set_visible(False)
		self.plt4.get_xaxis().set_visible(False)
		self.plt4.get_yaxis().set_visible(False)
		self.plt5.get_xaxis().set_visible(False)
		self.plt5.get_yaxis().set_visible(False)
		self.plt6.get_xaxis().set_visible(False)
		self.plt6.get_yaxis().set_visible(False)
		self.plt1.set_facecolor('#C6d3e0')
		self.plt2.set_facecolor('#C6d3e0')
		self.plt3.set_facecolor('#C6d3e0')
		self.plt4.set_facecolor('#C6d3e0')
		self.plt5.set_facecolor('#C6d3e0')
		self.plt6.set_facecolor('#C6d3e0')

		self.corr_window_layout.setContentsMargins(0,0,0,0)
		self.corr_window_layout.setContentsMargins(0,0,0,0)
		self.corr_window_layout.setContentsMargins(0,0,0,0)
		corrTopRow.setSpacing(16)
		self.corrBotRow.setSpacing(16)
		panel_third_row_btns.setSpacing(16)
		

		

				
		self.multiSelect = GateScanFileList(self,self.par_obj)

		self.update_correlation_parameters()
	def toggle_carpet_browser_fn(self):
		if self.toggle_carpet_state == 1:
			self.right_panel.addWidget(self.modelTab2)
			self.toggle_carpet_state = 0
			self.carpet_browser.hide()
		else: 
			self.carpet_browser.setCentralWidget(self.modelTab2)
			self.toggle_carpet_state = 1
			
			self.carpet_browser.show()

	def clear_region_fn(self):
		if self.par_obj.numOfLoaded == 0:
			return
		self.clickedS1 = 0 
		self.clickedS2 = self.carpet_img.shape[1]
		try:
			self.line.remove()
		except:
			pass
		self.draw_single_line()
	def export_all_data_fn(self):
		counter = 0;
		for objId in self.par_obj.objectRef:
			self.export_the_track(objId)
			counter = counter+1
			self.image_status_text.showMessage("Exporting carpet: "+str(counter)+' of '+str(self.par_obj.objectRef.__len__())+' selected.')
			self.fit_obj.app.processEvents()
			
	
	def bleachCorr1fn(self):
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				if objId.bleachCorr1 == True or objId.bleachCorr2 == True:
					if self.bleach_corr_on == True:
						#The bleach correction is on now we turn it off.
						self.bleach_corr_on_off.setText('  OFF  ')
						self.bleach_corr_on_off.setStyleSheet("color: red");
						self.bleach_corr_on = False
						self.plotDataQueueFn()
					else:
						#The bleach correction is off now we turn it on.
						if objId.bleachCorr1 == True:
							self.bleach_corr_on_off.setText('M1 ON ')
						if objId.bleachCorr2 == True:
							self.bleach_corr_on_off.setText('M2 ON ')
						self.bleach_corr_on_off.setStyleSheet("color: green");
						self.bleach_corr_on = True
						self.plotDataQueueFn()
				
						
						

		
	
				
						

						
					
		


	def update_correlation_parameters(self):
		""""""
		self.par_obj.spatialBin = int(self.spatialBinEdit.value())
		self.par_obj.m = float(self.mEdit.text())
		self.par_obj.int_time = int(self.kcountBinEdit.value())
		
		
	def CH0AutoFn(self):
		"""We change the view of the carpetDisplay to the auto-correlation channel 0. """
		
		self.carpetDisplay = 0
		self.CH0Auto_btn.setStyleSheet(" color: green")
		self.CH1Auto_btn.setStyleSheet(" color: black")
		self.CH01Cross_btn.setStyleSheet(" color: black")

		if self.par_obj.numOfLoaded == 0:
			return
		self.plotDataQueueFn()

	def CH1AutoFn(self):
		if self.par_obj.numOfLoaded == 0:
			return
		"""We change the view of the carpetDisplay to the auto-correlation channel 1. """
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				if objId.numOfCH ==2:
					self.carpetDisplay = 1
					self.plotDataQueueFn()
					self.CH0Auto_btn.setStyleSheet(" color: black")
					self.CH1Auto_btn.setStyleSheet(" color: green")
					self.CH01Cross_btn.setStyleSheet(" color: black")

	def CH01CrossFn(self):
		if self.par_obj.numOfLoaded == 0:
			return
		"""We change the view of the carpetDisplay to the cross-correlation channel 0 to 1. """
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				if objId.numOfCH ==2:
					self.carpetDisplay = 2
					self.plotDataQueueFn()
					self.CH0Auto_btn.setStyleSheet(" color: black")
					self.CH1Auto_btn.setStyleSheet(" color: black")
					self.CH01Cross_btn.setStyleSheet(" color: green")
	def save_log_carpets(self):
		"""Saves the carpet raw data to an image file"""
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				

				metadata = dict(microscope='george', shape=self.carpet_img.shape, dtype=self.carpet_img.dtype.str)
				#print(data.shape, data.dtype, metadata['microscope'])

				metadata = json.dumps(metadata)

				tif_fn.imsave(self.folderOutput.filepath+'/'+objId.name+'.tif', self.carpet_img.astype(np.float32), description=metadata)
	def save_raw_carpet_fn(self):
		"""Saves the carpet raw data to an image file"""
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				height = objId.CH0.shape[0]
				width = objId.CH0.shape[1]
				
				if objId.numOfCH ==1:
					
						export_im =np.zeros((height,width))
						export_im[:,:] = objId.CH0

				if objId.numOfCH ==2:
					
						export_im =np.zeros((2,height,width))
						export_im[0,:,:] =  objId.CH0
						export_im[1,:,:] =  objId.CH1
						

				metadata = dict(microscope='', shape=export_im.shape, dtype=export_im.dtype.str)
				#print(data.shape, data.dtype, metadata['microscope'])

				metadata = json.dumps(metadata)

				tif_fn.imsave(self.folderOutput.filepath+'/'+objId.name+'_raw.tif', export_im.astype(np.float32), description=metadata)

	def save_carpets(self):
		"""Saves the carpet raw data to an image file"""
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				height = objId.AutoCorr_carpetCH0.shape[1]
				width = objId.AutoCorr_carpetCH0.shape[0]
				
				self.plot_PhotonCount(objId)
				if objId.numOfCH ==1:
					if objId.bleachCorr1 == True or objId.bleachCorr2 == True:
						export_im =np.zeros((2,height,width))
						export_im[0,:,:] = objId.AutoCorr_carpetCH0[:,:].T;
						pbc = objId.AutoCorr_carpetCH0_pc[:,:].T;
						export_im[1,:pbc.shape[0],:pbc.shape[1]] = objId.AutoCorr_carpetCH0_pc[:,:].T;
					else:
						export_im =np.zeros((height,width))
						export_im[:,:] = objId.AutoCorr_carpetCH0[:,:].T;

				if objId.numOfCH ==2:
					if objId.bleachCorr1 == True or objId.bleachCorr2 == True:
						export_im =np.zeros((5,height,width))
						export_im[0,:,:] = objId.AutoCorr_carpetCH0[:,:].T;
						pbc = objId.AutoCorr_carpetCH0_pc[:,:].T;
						export_im[1,:pbc.shape[0],:pbc.shape[1]] = pbc
						export_im[2,:,:] = objId.AutoCorr_carpetCH1[:,:].T;
						pbc = objId.AutoCorr_carpetCH1_pc[:,:].T;
						export_im[3,:pbc.shape[0],:pbc.shape[1]] = pbc
						pbc = objId.CrossCorr_carpet01_pc[:,:].T;
						export_im[4,:pbc.shape[0],:pbc.shape[1]] = pbc
					else:
						export_im =np.zeros((3,height,width))
						export_im[0,:,:] = objId.AutoCorr_carpetCH0[:,:].T;
						export_im[1,:,:] = objId.AutoCorr_carpetCH1[:,:].T;
						export_im[2,:,:] = objId.CrossCorr_carpet01[:,:].T;

				metadata = dict(microscope='george', shape=export_im.shape, dtype=export_im.dtype.str)
				#print(data.shape, data.dtype, metadata['microscope'])

				metadata = json.dumps(metadata)

				tif_fn.imsave(self.folderOutput.filepath+'/'+objId.name+'.tif', export_im.astype(np.float32), description=metadata)

	def save_figure(self):
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				self.figure1.savefig(self.folderOutput.filepath+'/'+objId.name+'_fig.tif',
				orientation='portrait', papertype=None, format=None,
				transparent=False, bbox_inches=None, pad_inches=0.1,
				frameon=None)
		
	def prev_pane_fn(self):
		#Check all the loaded data and then adjust the pane accordingly
		updated = False
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				if objId.pane > 0:
					objId.pane = objId.pane -1
					self.plot_PhotonCount(objId)
					updated = True
		if updated == True:
			self.plotDataQueueFn()
	def next_pane_fn(self):
		#Check all the loaded data and then adjust the pane accordingly
		updated = False
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				if objId.pane < objId.maxPane:
					objId.pane = objId.pane +1
					self.plot_PhotonCount(objId)
					updated = True
		if updated == True:
			self.plotDataQueueFn()
	def reprocessDataFn(self):

		if self.par_obj.numOfLoaded == 0:
			return
		self.update_correlation_parameters()
		for objId in self.par_obj.objectRef:
					objId.processData()
					objId.bleachCorr1 = False
					objId.bleachCorr2 = False

		self.bleach_corr_on = False
		self.bleach_corr_on_off.setText('  OFF  ')
		self.bleach_corr_on_off.setStyleSheet(" color: red");
		self.plotDataQueueFn();
		self.plot_PhotonCount(objId)
		

	def plotDataQueueFn(self):
		self.plt1.cla()
		self.plt2.cla()
		self.plt3.cla()
		self.plt5.clear()
		self.canvas1.draw()
		self.canvas5.draw()
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				self.plot(objId)
				self.plot_PhotonCount(objId)

		self.plt5.get_xaxis().set_visible(True)
		self.plt5.get_yaxis().set_visible(True)
		#self.plt1.set_ylim(bottom=0)
		#self.plt5.ax = plt.gca()
		#self.plt5.a.freshDraw()
	def plot_PhotonCount(self,objId):
		"""Plots the photon counting"""
		
		self.plt4.clear()
		self.canvas4.draw()

		if objId !=None:

			
			if self.clickedS1== None:
				xmin = 0
				xmax = objId.kcountCH0.__len__()-1
			else:
				xmin = int(self.clickedS1)
				xmax = int(self.clickedS2)-1
			if xmin >xmax:
				xtemp = xmax
				xmax = xmin
				xmin = xtemp

			self.int_time_trace_mode = 'global'
			
			if self.int_time_trace_mode == 'global':
				
				#If just one line is highlighted.
				
				if xmin == xmax:
					if  self.bleach_corr_on  == True and objId.bleachCorr1 == True:
						totalFn = objId.CH0_pc[:,xmin]
					else:
						totalFn = objId.CH0[:,xmin]
				else:
					if  self.bleach_corr_on  == True and objId.bleachCorr1 == True:
						totalFn = np.sum(objId.CH0_pc[:,xmin:xmax], 1).astype(np.float64)
					else: 
						totalFn = np.sum(objId.CH0[:,xmin:xmax], 1).astype(np.float64)
				
				self.plt4.plot(np.arange(0,totalFn.shape[0],10)*objId.deltat ,totalFn[0::10],color=objId.color, linewidth=1)
				if self.bleach_corr_on:

					self.plt4.text(0,self.plt4.get_ylim()[0]+1,  'photobleaching correction on',dict(color='green', alpha=0.5))
				
				if objId.numOfCH == 2:
					#If just one line is highlighted.
					if xmin == xmax:
						if  self.bleach_corr_on  == True and objId.bleachCorr1 == True:
							totalFn = objId.CH1_pc[:,xmin]
						else:
							totalFn = objId.CH1[:,xmin]
					else:
						if  self.bleach_corr_on  == True and objId.bleachCorr1 == True:
							totalFn = np.sum(objId.CH1_pc[:,xmin:xmax], 1).astype(np.float64)
						else:
							totalFn = np.sum(objId.CH1[:,xmin:xmax], 1).astype(np.float64)
					
					self.plt4.plot(np.arange(0,totalFn.shape[0],10)*objId.deltat ,totalFn[0::10],'grey', linewidth=1)
			
			if self.int_time_trace_mode == 'first_pane':
				yLimMn = int(((objId.pane)*(objId.CH0.shape[1]/64)*150))
				yLimMx = int(((objId.pane+1)*(objId.CH0.shape[1]/64)*150))
				
				#If just one line is highlighted.
				if xmin == xmax:
					totalFn = objId.CH0[:,xmin]
				else:
					totalFn = np.sum(objId.CH0[:,xmin:xmax], 1).astype(np.float64)
				self.plt4.plot(np.arange(yLimMn,yLimMx)*objId.deltat ,totalFn[yLimMn:yLimMx],color=objId.color, linewidth=1)
				#If two channels are present
				if objId.numOfCH == 2:
					if xmin == xmax:
						totalFn = objId.CH1[:,xmin]
					else:
						totalFn = np.sum(objId.CH1[:,xmin:xmax], 1).astype(np.float64)
					self.plt4.plot(np.arange(yLimMn,yLimMx)*objId.deltat ,totalFn[yLimMn:yLimMx],color='grey', linewidth=1)


		self.figure4.subplots_adjust(bottom=0.15,right=0.95)
		self.plt4.tick_params(axis='both', which='major', labelsize=8)
		#self.figure4.tight_layout(pad=1.08)

		self.plt4.set_xlabel('Time (ms) ', fontsize=8)
		if objId !=None:
			if objId.numOfCH == 2:
				self.plt4.set_ylabel('Intensity Counts (CH0 ('+objId.color+'), CH1 (grey))', fontsize=4)
			else:
				self.plt4.set_ylabel('Intensity Counts (CH0 ('+objId.color+'))', fontsize=6)
		self.plt4.xaxis.grid(True,'minor')
		self.plt4.xaxis.grid(True,'major')
		self.plt4.yaxis.grid(True,'minor')
		self.plt4.yaxis.grid(True,'major')
		self.plt4.get_xaxis().set_visible(True)
		self.plt4.get_yaxis().set_visible(True)
		

		self.plt4.set_autoscale_on(False)
		self.canvas4.draw()

			
	def plot(self,objId):
		''' plots correlation functions '''

		self.autotime = objId.autotime
		auto = objId.autoNorm
		corrText = 'Auto-correlation'
		
		#Where the selected pixel correlation functions are plotted as 2D.
		self.plt1.plot(self.autotime,auto[:,0,0],objId.color, linewidth=1)
		self.plt1.set_xscale('log')
		self.plt1.set_xlabel('Pixels', fontsize=12)
		self.plt1.set_ylabel(corrText+' CH0', fontsize=12)
		self.plt1.xaxis.grid(True,'minor')
		self.plt1.xaxis.grid(True,'major')
		self.plt1.yaxis.grid(True,'minor')
		self.plt1.yaxis.grid(True,'major')

		
		

		#The span function which changes the carpet visualisation.
		self.span1 = SpanSelector(self.plt1, self.setCarpetExposure, 'horizontal', useblit=True, minspan =0, rectprops=dict(edgecolor='black',alpha=1.0, facecolor='None') )		
		
		yLimMn = int((objId.pane)*(objId.CH0.shape[1]/64)*150)
		yLimMx = int((objId.pane+1)*(objId.CH0.shape[1]/64)*150)
		

		
		if objId.numOfCH == 1:
			#This is for the raw intensity trace of the data (XT carpet).
			XTcarpet=np.flipud(objId.CH0[yLimMn:yLimMx,:].T)
			#This is for the main correlation carpet display. If you move from a two colour image to a one colour one.
			self.carpetDisplay = 0
			self.CH0Auto_btn.setStyleSheet(" color: green")
			self.CH1Auto_btn.setStyleSheet(" color: black")
			self.CH01Cross_btn.setStyleSheet(" color: black")

		elif objId.numOfCH == 2:
			#This is for the raw intensity trace of the data (XT carpet).
			XTcarpet = np.zeros((objId.CH0.shape[1],yLimMx-yLimMn,3))
			XTcarpet[:,:,0]=np.flipud(objId.CH0[yLimMn:yLimMx,:].T)
			XTcarpet[:,:,1]=np.flipud(objId.CH1[yLimMn:yLimMx,:].T)
		
		XTcarpet_norm = (XTcarpet)/np.max(XTcarpet)
	
		XTcarpet_fig = self.plt5.imshow((XTcarpet_norm),interpolation = 'nearest',extent=[yLimMn,yLimMx,0,objId.CH0.shape[1]])
		#colbar = self.figure5.colorbar(XTcarpet_fig,self)
		#colbar.set_label('Scale (norm. to pix max)')
		self.plt5.get_xaxis().set_visible(True)
		self.plt5.get_yaxis().set_visible(True)
		self.figure5.subplots_adjust(bottom =0.25,left=0.1,right=0.95)
		self.plt5.set_xlabel('Scan line ('+str(np.round(objId.deltat,2))+') ms', fontsize=8)
		self.plt5.set_ylabel('Column pixels', fontsize=12)
		self.plt5.tick_params(axis='both', which='major', labelsize=8)
		self.plt5.autoscale(False)
		self.canvas5.draw()




		
		#Checks which channel is displayed and then loads the relevant carpet.
		if self.bleach_corr_on == True:
			
			#This is for the photo-corrected version of the carpets.
			if self.carpetDisplay == 0:
				img =objId.AutoCorr_carpetCH0_pc[:,:];
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale_pc
			if self.carpetDisplay == 1:
				img = objId.AutoCorr_carpetCH1_pc[:,:];
				sum_img = np.flipud(objId.CH1_arrayColSum)
				carp_scale = objId.corrArrScale_pc
			if self.carpetDisplay == 2:
				img = objId.CrossCorr_carpet01_pc[:,:];
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale_pc
		else:
			if self.carpetDisplay == 0:
				img = objId.AutoCorr_carpetCH0[:,:]
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale
			if self.carpetDisplay == 1:
				img =objId.AutoCorr_carpetCH1[:,:]
				sum_img = np.flipud(objId.CH1_arrayColSum)
				carp_scale = objId.corrArrScale
			if self.carpetDisplay == 2:
				img = objId.CrossCorr_carpet01[:,:]
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale

		self.carpet_img = np.copy(img) #Important to copy as img is pointer to original.
		
		self.carpet_img[self.carpet_img < 0]=0;
		for i in range(0, img.shape[1]):
			npmax = np.max(self.carpet_img[:,i])
			if npmax != 0:
				self.carpet_img[:,i] = self.carpet_img[:,i]/npmax

		self.plt2.set_xlabel('Lag time (ms)', fontsize=12)
		self.plt2.set_xscale('log')
		#print 'mesh',img.shape[1]
		#print 'carp',self.carpet_img.shape
		X, Y = np.meshgrid(np.arange(0,img.shape[1]+1),carp_scale)
		self.corr_carpet = self.plt2.pcolormesh(Y,X,self.carpet_img,cmap='jet')
		self.plt2.set_xlim(0,objId.corrArrScale[-1])

		#Plot the interpolation iensity profile to the left.
		im1 = self.plt3.imshow(sum_img.reshape(objId.CH0_arrayColSum.shape[0],1),extent=[0,5,0,img.shape[1]],interpolation = 'nearest',aspect='auto',cmap=cm.Reds_r);
		self.plt3.set_ylabel('Column pixels')
		self.plt3.set_xlabel('Intensity\nmaxima')
		self.plt3.set_xticklabels('')
		#if self.bleach_corr_on:
		#	self.plt2.text(0, 0, 'photobleaching correction on',transform=self.plt2.transAxes,withdash=True)
		if self.bleach_corr_on:
			self.plt1.text(0, 0.1, 'photobleaching correction on',transform=self.plt1.transAxes,withdash=True,fontdict=dict(color='green', alpha=0.5,fontsize=18))

		self.canvas1.draw()
		self.plt1.cla()
		
		
		
		colbar = self.figure1.colorbar(self.corr_carpet, cax=self.plt6)
		colbar.set_label('Scale (norm. to pix max)')
		
		self.span2 = SpanSelector(self.plt2, self.onselect, 'vertical', useblit=True, minspan =0, rectprops=dict(edgecolor='black',alpha=1.0, facecolor='None') )
		if self.clickedS1 and self.clickedS2 != None:
			self.onselect(self.clickedS1, self.clickedS2)
			self.plt2.set_ylim([0,img.shape[1]])
		
		if self.clim_low != 0 and self.clim_high != None:
			self.corr_carpetset_clim((0,np.max(imgN)))
		
		self.figure1.subplots_adjust(left=0.1,right=0.90)
		self.plt2.autoscale(False)
		
		self.plt1.get_xaxis().set_visible(True)
		self.plt1.get_yaxis().set_visible(True)
		self.plt2.get_xaxis().set_visible(True)
		self.plt2.get_yaxis().set_visible(True)
		self.plt3.get_xaxis().set_visible(True)
		self.plt3.get_yaxis().set_visible(True)
		self.plt5.get_xaxis().set_visible(True)
		self.plt5.get_yaxis().set_visible(True)
		self.plt6.get_xaxis().set_visible(True)
		self.plt6.get_yaxis().set_visible(True)
		
		
		# refresh canvas
		self.canvas1.draw()
	def setCarpetExposure(self,pix_sel_hgh,pix_sel_low):

		if pix_sel_hgh < pix_sel_low:
			temp = pix_sel_low
			pix_sel_low = pix_sel_hgh
			pix_sel_low = temp
		#Upon dragging a span on the correlation profile the intensity of the correlation carpet is updated.
		
		#Find the nearest value and its corresponding index in the scale
		cmin_ind = int(np.argmin(np.abs(self.autotime -  pix_sel_low)))
		cmax_ind = int(np.argmin(np.abs(self.autotime -  pix_sel_hgh)))
		
		
		cmin  = np.min(self.carpet_img[cmin_ind,:])
		cmax  = np.max(self.carpet_img[cmax_ind,:])
		

		self.corr_carpet.set_clim((cmin,cmax))
		self.canvas1.draw()
		
	def saveRegion(self):
		"""Saves the pixel selection for export. """
		
		if self.par_obj.numOfLoaded == 0:
			return
		
		#Appends value to array
		self.multiSelect.x0.append( self.clickedS2)
		self.multiSelect.x1.append( self.clickedS1)
		self.multiSelect.color = self.par_obj.colors[self.multiSelect.rect.__len__()]
		self.multiSelect.TGid.append(self.par_obj.TGnumOfRgn)
		self.multiSelect.facecolor.append(self.par_obj.colors[self.par_obj.TGnumOfRgn.__len__()])
		self.par_obj.TGnumOfRgn.append(self.par_obj.TGnumOfRgn.__len__())
		#Regenerates list.
		self.multiSelect.generateList()
	
	def onselect(self,vmin, vmax):
			
			self.x0 = vmin
			self.x1 = vmax
			
			if(self.x0 <0): self.x0 =0
			if(self.x1 <0): self.x1 =0
			if(self.x0 >self.x1): 
				self.x1b =self.x0;
				self.x0=self.x1;
				self.x0=self.x1b
			#Corner case fix. If a line is inherited beyond the dimensions of the present carpet.
			if self.x1 > self.carpet_img.shape[1]:
				self.x1 = int(np.floor(self.carpet_img.shape[1]/2)+0.5)
				self.x0 = int(np.floor(self.carpet_img.shape[1]/2)-0.5)

			self.clickedS1 = int(np.floor(self.x0))
			self.clickedS2 = int(np.ceil(self.x1))
			try:
				self.line.remove()
			except:
				pass
			self.line = self.plt2.axhspan(self.x0, self.x1, facecolor=None,fill=False, alpha=1.0)
			
			
			self.draw_single_line()
	def draw_single_line(self):
				self.plt1.cla()

				#self.par_obj.plt1.set_autoscale_on(True)
				for objId in self.par_obj.objectRef:

					if(objId.cb.isChecked() == True):
						self.plot_PhotonCount(objId)
				
						self.plt1.set_xscale('log');
						self.plt1.set_ylabel('Correlation', fontsize=12)
						if self.bleach_corr_on:
							self.plt1.text(0.1, 0.1, 'photobleaching correction on',transform=self.plt1.transAxes,withdash=True,fontdict=dict(color='green', alpha=0.5,fontsize=14))

						if self.clickedS1 != None  and self.clickedS2 != None:
							for b in range(self.clickedS1,self.clickedS2):
								self.plt1.set_autoscale_on(True)
								#Is the button checked.
								if self.bleach_corr_on == True:
									if self.carpetDisplay == 0:
										self.plt1.plot(objId.corrArrScale_pc, objId.AutoCorr_carpetCH0_pc[:,int(b)],objId.color, linewidth=1)
									if self.carpetDisplay == 1:
										self.plt1.plot(objId.corrArrScale_pc, objId.AutoCorr_carpetCH1_pc[:,int(b)],objId.color, linewidth=1)
									if self.carpetDisplay == 2:
										self.plt1.plot(objId.corrArrScale_pc, objId.CrossCorr_carpet01_pc[:,int(b)],objId.color, linewidth=1)
								else:
									if self.carpetDisplay == 0:
										self.plt1.plot(objId.corrArrScale ,objId.AutoCorr_carpetCH0[:,int(b)],objId.color, linewidth=1)
									if self.carpetDisplay == 1:
										self.plt1.plot(objId.corrArrScale ,objId.AutoCorr_carpetCH1[:,int(b)],objId.color, linewidth=1)
									if self.carpetDisplay == 2:
										self.plt1.plot(objId.corrArrScale ,objId.CrossCorr_carpet01[:,int(b)],objId.color, linewidth=1)
								
								a,c = self.plt1.get_ylim()
								self.plt1.set_ylim(bottom=0,top=c)

							self.canvas1.draw()
				
	def export_track_to_fit(self):

		
		self.export_track_fn()
	def save_as_specific_csv(self,xmin,xmax):
		if self.par_obj.numOfLoaded == 0:
			return
		for objId in self.par_obj.objectRef:
			
			if(objId.cb.isChecked() == True):
				self.save_as_csv(objId,xmin,xmax)
	def save_all_as_csv_fn(self):
		if self.par_obj.numOfLoaded == 0:
			return
		objId = self.par_obj.objectRef[0]
		if self.clickedS1== None:
			xmin = 0
			xmax = objId.kcountCH0.__len__()-1
		else:
			xmin = int(self.clickedS1)
			xmax = int(self.clickedS2)-1
		if xmin >xmax:
			xtemp = xmax
			xmax = xmin
			xmin = xtemp
		#Checks if the plot is on or not.
		for objId in self.par_obj.objectRef:
			
				self.save_as_csv(objId,xmin,xmax)
	def save_as_csv(self,objId,xmin,xmax):
		#xmin = int(self.clickedS1)
		#xmax = int(self.clickedS2)-1
		#Checks if the plot is on or not.
				parent_name = objId.name
				parent_uqid = uuid.uuid4()
		
				
				for i in range(xmin, xmax+1):
					
					path = os.path.join(self.folderOutput.filepath,objId.name+'_'+str(i)+'_correlation.csv')

					f = open(path, 'w')
					f.write('version,'+str(2)+'\n')
					f.write('numOfCH,'+str(objId.numOfCH)+'\n')
					f.write('type, scan\n')
					
					if objId.numOfCH == 1:
						f.write('ch_type,'+str(0)+'\n')
						
						#f.write('CV,'+str(objId.CV[i])+'\n')
						f.write('carpet pos,'+str(i)+'\n')
						f.write('parent_name,'+str(parent_name)+'\n')
						f.write('parent_uqid,'+str(parent_uqid)+'\n')
						f.write('parent_filename,'+str(objId.file_name)+'\n')
						
						if self.bleach_corr_on == True:
							if objId.bleachCorr1 == True:
								f.write('pc, 1\n');
								f.write('pbc_f0,'+str(objId.pbc_f0_ch0)+'\n');
								f.write('pbc_tb,'+str(objId.pbc_tb_ch0)+'\n');
								f.write('kcount,'+str(objId.kcountCH0_pc[i])+'\n')
								f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+'\n')
								f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+'\n')
							
							if objId.bleachCorr2 == True: 
								f.write('pc, 2\n');
								f.write('kcount,'+str(objId.kcountCH0_pc[i])+'\n')
								f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+'\n')
								f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+'\n')
						
						
						
							f.write('Time (ms), CH0 Auto-Correlation\n')
							for x in range(0,objId.corrArrScale_pc.shape[0]):
								f.write(str(float(objId.corrArrScale_pc[x]))+','+str(objId.AutoCorr_carpetCH0_pc[x,i])+ '\n')
						else:
							f.write('pc, 0\n');
							f.write('kcount,'+str(objId.kcountCH0[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0[i])+'\n')
							f.write('Time (ms), CH0 Auto-Correlation\n')
							for x in range(0,objId.corrArrScale.shape[0]):
								f.write(str(float(objId.corrArrScale[x]))+','+str(objId.AutoCorr_carpetCH0[x,i])+ '\n')
						f.write('end\n')
						
					if objId.numOfCH == 2:
						f.write('ch_type, 0 ,1, 2\n')
						
						f.write('carpet pos,'+str(i)+'\n')
						f.write('parent_name,'+str(parent_name)+'\n')
						f.write('parent_uqid,'+str(parent_uqid)+'\n')
						f.write('parent_filename,'+str(objId.file_name)+'\n')

						if self.bleach_corr_on == True:
							if objId.bleachCorr1 == True:
								f.write('pc, 1\n');
								f.write('pbc_f0,'+str(objId.pbc_f0_ch0)+','+str(objId.pbc_f0_ch1)+'\n');
								f.write('pbc_tb,'+str(objId.pbc_tb_ch0)+','+str(objId.pbc_tb_ch1)+'\n');
								f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+','+str(objId.numberNandBCH1_pc[i])+'\n')
								f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+','+str(objId.brightnessNandBCH1_pc[i])+'\n')
								f.write('CV,'+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+'\n')
							if objId.bleachCorr2 == True:
							
								f.write('pc, 2\n');
								f.write('kcount,'+str(objId.kcountCH0_pc[i])+','+str(objId.kcountCH1_pc[i])+'\n')
								f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+','+str(objId.numberNandBCH1_pc[i])+'\n')
								f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+','+str(objId.brightnessNandBCH1_pc[i])+'\n')
								f.write('CV,'+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+'\n')
						
							f.write('Time (ms), CH0 Auto-Correlation, CH1 Auto-Correlation, CH01 Cross-Correlation\n')
							for x in range(0,objId.corrArrScale_pc.shape[0]):
								f.write(str(float(objId.corrArrScale_pc[x]))+','+str(objId.AutoCorr_carpetCH0_pc[x,i])+','+str(objId.AutoCorr_carpetCH1_pc[x,i])+','+str(objId.CrossCorr_carpet01_pc[x,i])+ '\n')
						else:
							f.write('pc, 0\n');
							f.write('kcount,'+str(objId.kcountCH0[i])+','+str(objId.kcountCH1[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0[i])+','+str(objId.numberNandBCH1[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0[i])+','+str(objId.brightnessNandBCH1[i])+'\n')
							f.write('CV,'+str(objId.CV[i])+','+str(objId.CV[i])+','+str(objId.CV[i])+'\n')
							f.write('Time (ms), CH0 Auto-Correlation, CH1 Auto-Correlation, CH01 Cross-Correlation\n')
							for x in range(0,objId.corrArrScale.shape[0]):
								f.write(str(float(objId.corrArrScale[x]))+','+str(objId.AutoCorr_carpetCH0[x,i])+','+str(objId.AutoCorr_carpetCH1[x,i])+','+str(objId.CrossCorr_carpet01[x,i])+'\n')
						f.write('end\n')
					f.close()
						






		
		# if self.objId.numOfCH == 2:
		# 	f = open(self.win_obj.folderOutput.filepath+'/'+self.objId.name+'_correlation.csv', 'w')
		# 	f.write('# Time (ms),CH0 Auto-Correlation, CH1 Auto-Correlation, CC01 Auto-Correlation, CC10 Auto-Correlation\n')
		# 	for x in range(0,self.objId.autotime.shape[0]):
		# 		f.write(str(int(self.objId.autotime[x]))+','+str(self.objId.autoNorm[x,0,0])+','+str(self.objId.autoNorm[x,1,1])+','+str(self.objId.autoNorm[x,0,1])+','+str(self.objId.autoNorm[x,1,0])+ '\n')

		# print 'file Saved'
	def export_track_fn(self):

		#Checks if the plot is on or not.
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				self.export_the_track(objId)	
	def export_the_track(self,objId):
				
		if self.clickedS1== None:
			xmin = 0
			xmax = objId.kcountCH0.__len__()-1
		else:
			xmin = int(self.clickedS1)
			xmax = int(self.clickedS2)-1
		if xmin >xmax:
			xtemp = xmax
			xmax = xmin
			xmin = xtemp
		

		parent_name = objId.name
		parent_uqid = uuid.uuid4()



		for i in range(xmin, xmax+1):
			#print i
			corrObj1 = corrObject(objId.filepath,self.fit_obj);
			corrObj1.siblings = None
			corrObj1.parent_name = parent_name
			corrObj1.parent_uqid = parent_uqid
			corrObj1.file_name = objId.file_name

			self.fit_obj.objIdArr.append(corrObj1.objId)
			corrObj1.param = copy.deepcopy(self.fit_obj.def_param)
			corrObj1.ch_type = 0
			corrObj1.prepare_for_fit()
			
			
			
			corrObj1.type = "scan"
			corrObj1.siblings = None
			corrObj1.item_in_list = False

			if self.bleach_corr_on == True:
				corrObj1.kcount = objId.kcountCH0_pc[i]
				corrObj1.numberNandB = objId.numberNandBCH0_pc[i]
				corrObj1.brightnessNandB = objId.brightnessNandBCH0_pc[i]
				
				corrObj1.name = objId.name+'row_'+str(i)+'_CH0_Auto_Corr_pc'
				corrObj1.autotime = objId.corrArrScale_pc[:]
				corrObj1.autoNorm = objId.AutoCorr_carpetCH0_pc[:,i]
				corrObj1.max = np.max(objId.AutoCorr_carpetCH0_pc[:,i])
				corrObj1.min = np.min(objId.AutoCorr_carpetCH0_pc[:,i])
				if objId.bleachCorr1 == True:
					#Additional parameters from photobleaching method 1
					corrObj1.pbc_f0 = objId.pbc_f0_ch0
					corrObj1.pbc_tb = objId.pbc_tb_ch0
			else:
				corrObj1.kcount = objId.kcountCH0[i]
				corrObj1.numberNandB = objId.numberNandBCH0[i]
				corrObj1.brightnessNandB = objId.brightnessNandBCH0[i]
				corrObj1.s2n = objId.s2nCH0[i]
				corrObj1.name = objId.name+'row_'+str(i)+'_CH0_Auto_Corr'
				corrObj1.autotime = objId.corrArrScale[:]
				corrObj1.autoNorm = objId.AutoCorr_carpetCH0[:,i]
				corrObj1.max = np.max(objId.AutoCorr_carpetCH0[:,i])
				corrObj1.min = np.min(objId.AutoCorr_carpetCH0[:,i])
			corrObj1.tmax = np.max(corrObj1.autotime)
			corrObj1.tmin = np.min(corrObj1.autotime)
			
			
			if objId.numOfCH == 2:
				corrObj2 = corrObject(objId.filepath,self.fit_obj);
				corrObj2.siblings = None
				corrObj2.parent_name = parent_name
				corrObj2.parent_uqid = parent_uqid
				corrObj2.file_name = objId.file_name
				self.fit_obj.objIdArr.append(corrObj2.objId)
				corrObj2.ch_type = 1
				corrObj2.param = copy.deepcopy(self.fit_obj.def_param)
				corrObj2.prepare_for_fit()
				corrObj2.autotime = objId.corrArrScale[:]
				corrObj2.item_in_list = False

				
				
				corrObj1.CV = objId.CV[i]
				corrObj2.CV = objId.CV[i]
				corrObj2.type = "scan"
				if self.bleach_corr_on == True:
					corrObj2.kcount = objId.kcountCH1_pc[i]
					corrObj2.numberNandB = objId.numberNandBCH1_pc[i]
					corrObj2.brightnessNandB = objId.brightnessNandBCH1_pc[i]
					corrObj2.name = objId.name+'row_'+str(i)+'_CH1_Auto_Corr_pc'
					corrObj2.autotime =	objId.corrArrScale_pc
					corrObj2.autoNorm = objId.AutoCorr_carpetCH1_pc[:,i]
					corrObj2.max = np.max(objId.AutoCorr_carpetCH1_pc[:,i])
					corrObj2.min = np.min(objId.AutoCorr_carpetCH1_pc[:,i])
					

					if objId.bleachCorr1 == True:
						#Additional parameters from photobleaching method 1
						corrObj2.pbc_f0 = objId.pbc_f0_ch1
						corrObj2.pbc_tb = objId.pbc_tb_ch1
				else:
					corrObj2.kcount = objId.kcountCH1[i]
					corrObj2.numberNandB = objId.numberNandBCH1[i]
					corrObj2.brightnessNandB = objId.brightnessNandBCH1[i]
					corrObj2.s2n = objId.s2nCH1[i]
					corrObj2.name = objId.name+'row_'+str(i)+'_CH1_Auto_Corr'
					corrObj2.autoNorm = objId.AutoCorr_carpetCH1[:,i]
					corrObj2.max = np.max(objId.AutoCorr_carpetCH1[:,i])
					corrObj2.min = np.min(objId.AutoCorr_carpetCH1[:,i])
				corrObj2.tmax = np.max(corrObj2.autotime)
				corrObj2.tmin = np.min(corrObj2.autotime)
				

				corrObj3 = corrObject(objId.filepath,self.fit_obj);
				corrObj3.siblings = None
				corrObj3.parent_name = parent_name
				corrObj3.parent_uqid = parent_uqid
				corrObj3.file_name = objId.file_name
				self.fit_obj.objIdArr.append(corrObj3.objId)
				corrObj3.item_in_list = False

				corrObj3.ch_type = 2
				corrObj3.param = copy.deepcopy(self.fit_obj.def_param)
				corrObj3.CV = objId.CV[i]
				corrObj3.prepare_for_fit()
				corrObj3.autotime = objId.corrArrScale[:]
				if self.bleach_corr_on == True:
					corrObj3.name = objId.name+'row_'+str(i)+'_CH01_Auto_Corr_pc'
					corrObj3.autotime =	objId.corrArrScale_pc
					corrObj3.autoNorm = objId.CrossCorr_carpet01_pc[:,i]
					corrObj3.max = np.max( objId.CrossCorr_carpet01_pc[:,i])
					corrObj3.min = np.min( objId.CrossCorr_carpet01_pc[:,i])
				else:
					corrObj3.name = objId.name+'row_'+str(i)+'_CH01_Auto_Corr'
					corrObj3.autoNorm = objId.CrossCorr_carpet01[:,i]
					corrObj3.max = np.max(objId.CrossCorr_carpet01[:,i])
					corrObj3.min = np.min(objId.CrossCorr_carpet01[:,i])
				corrObj3.tmax = np.max(corrObj3.autotime)
				corrObj3.tmin = np.min(corrObj3.autotime)
				corrObj3.param = copy.deepcopy(self.fit_obj.def_param)

				corrObj1.siblings = [corrObj2,corrObj3]
				corrObj2.siblings = [corrObj1,corrObj3]
				corrObj3.siblings = [corrObj1,corrObj2]

		self.fit_obj.fill_series_list()


		


class lineEditSp(QLineEdit):
	def __init__(self,text,win_obj,par_obj):
		QLineEdit.__init__(self,text)
		self.editingFinished.connect(self.__handleEditingFinished)
		self.par_obj = par_obj
		self.win_obj = win_obj
		self.obj = []
		self.type = []
		self.TGid =[]
	def __handleEditingFinished(self):
		if(self.type == 'm'):
			self.par_obj.m = float(self.text())
		
		if(self.type == 'tgt0' ):
			self.win_obj.multiSelect.x1[self.TGid] = float(self.text())
	
		if(self.type == 'tgt1' ):
			self.win_obj.multiSelect.x0[self.TGid] = float(self.text())

		if(self.type == 'name' ):
			self.obj.name = str(self.text())
		

		   
			
	  


			


class pushButtonSp(QPushButton):
	def __init__(self,text, win_obj,par_obj):
		QComboBox.__init__(self,text)
		self.clicked.connect(self.__activated)
		
		#Which list is should look at.
		self.objList = []
		self.xmin = []
		self.xmax =[]
		self.TGid = []
		self.par_obj = []
		self.win_obj = win_obj
		self.par_obj = par_obj
	def __activated(self):
		
		self.xmin = int(self.win_obj.multiSelect.x0[self.TGid])
		self.xmax = int(self.win_obj.multiSelect.x1[self.TGid])
		if self.xmin >self.xmax:
			xtemp = self.xmax
			self.xmax = self.xmin
			self.xmin = xtemp
		self.win_obj.export_track_fn()
		

						
class checkBoxSp3(QCheckBox):
	def __init__(self, par_obj, win_obj):
		QCheckBox.__init__(self)
		self.obj = []
		self.type = []
		self.name =[]
		self.par_obj = par_obj
		self.win_obj = win_obj
	def updateChecked(self):
		
		if self.isChecked() == True:  

			for objId in self.par_obj.objectRef:
				if objId != self.obj:
					objId.plotOn = False
					objId.cb.setChecked(False)
			

		
			self.win_obj.DeltatEdit.setText(str(self.obj.deltat));
			self.obj.plotOn = self.isChecked()
			
			
			
			if self.obj.bleachCorr1 == False and self.obj.bleachCorr2 == False:
				self.win_obj.bleach_corr_on_off.setText('  OFF  ')
				self.win_obj.bleach_corr_on_off.setStyleSheet("color: red");
				self.win_obj.bleach_corr_on = False
			
			
			self.win_obj.plotDataQueueFn()
		




class scanFileList():
	def __init__(self, win_obj, par_obj):
		
		self.subNum =0


		self.win_obj = win_obj
		
		
		self.par_obj = par_obj
		self.generateList()
		
	def generateList(self):
		
		self.obj =[];
		self.objCheck =[];
		self.win_obj.xb = []
		
		for i in range(0,self.par_obj.numOfLoaded):
			self.win_obj.modelTab2.setRowCount(i+1)
			#Represents each y
			self._l=QHBoxLayout()
			self.obj.append(self._l)

			
			#HTML text
			a =baseList()
			a.listId = i
			type_obj = self.par_obj.objectRef[i].type
			a.setText('<HTML><p style="color:'+str(self.par_obj.objectRef[i].color)+';margin-top:0">'+type_obj+' : </p></HTML>')
			

			self.win_obj.modelTab2.setCellWidget(i, 0, a)

			#Line edit for each entry in the file list
			lb = lineEditSp('',self.win_obj,self.par_obj)
			lb.type ='name'
			
			lb.obj = self.par_obj.objectRef[i]
			lb.setText(self.par_obj.objectRef[i].name);
			self.win_obj.modelTab2.setCellWidget(i, 1, lb)

			
			

			#Adds the plot checkBox:
			self.par_obj.objectRef[i].cb = checkBoxSp3(self.par_obj,self.win_obj)
			
			self.par_obj.objectRef[i].cb.setChecked(self.par_obj.objectRef[i].plotOn)
			self.par_obj.objectRef[i].cb.obj = self.par_obj.objectRef[i]
			self.par_obj.objectRef[i].cb.setChecked(False)
			self.par_obj.objectRef[i].cb.stateChanged.connect(self.par_obj.objectRef[i].cb.updateChecked)
			self.win_obj.modelTab2.setCellWidget(i, 2, self.par_obj.objectRef[i].cb)


			#Line edit for each entry in the file list
			lb2 = QLabel()
			lb2.setText(self.par_obj.objectRef[i].file_name);
			self.win_obj.modelTab2.setCellWidget(i, 3, lb2)

			
			#Adds save button to the file.
			#sb = pushButtonSp2('save file')
			#sb.par_obj = self.par_obj
			#sb.win_obj = self.win_obj
			#sb.objId = self.par_obj.objectRef[i]
			#self.win_obj.modelTab2.setCellWidget(i, 4, sb)

			#Adds save button to the file.
			xb =  pushButtonSp3('X')
			self.win_obj.xb.append(xb)
			self.win_obj.xb[-1].setToolTip('Remove File from scanning software.')
			self.win_obj.xb[-1].par_obj = self.par_obj
			self.win_obj.xb[-1].win_obj = self.win_obj
			self.win_obj.xb[-1].id = i
			self.win_obj.xb[-1].type = 'remove_file'
			self.win_obj.xb[-1].parent_id = self
			self.win_obj.modelTab2.setCellWidget(i, 4, self.win_obj.xb[-1])


			#The filename
			b = baseList()
			b.setText('<HTML><p style="margin-top:0">'+self.par_obj.objectRef[i].ext+' file :'+str(self.par_obj.objectRef[i].filepath)+' </p></HTML>')
			self.win_obj.modelTab2.setCellWidget(i, 5, b)
			
			
			#self.par_obj.label.objCheck.append(cb)
			j = i+1
		
		

class GateScanFileList():
	#Generates scroll box for time-gating data.
	def __init__(self, win_obj, par_obj):
		
		self.x0 =[]
		self.x1 =[]
		self.facecolor =[]
		self.TGid = []
		self.rect =[]
		self.par_obj = par_obj
		self.win_obj = win_obj

	def generateList(self):
		c = 0
		
		for i in self.par_obj.TGnumOfRgn:
				self.win_obj.modelTab.setRowCount(c+1)
				
				txt2 = QLabel()
				txt2.setText('<HTML><p style="color:'+str(self.par_obj.colors[i])+';margin-top:0">t0:</p></HTML>')
				self.win_obj.modelTab.setCellWidget(c, 0, txt2)


				lb1 = lineEditSp(str(self.x1[i]),self.win_obj,self.par_obj)
				lb1.setMaxLength(5)
				lb1.setFixedWidth(30)
				lb1.setText(str(self.x1[i]))
				lb1.type = 'tgt0'
				lb1.TGid = i
				self.win_obj.modelTab.setCellWidget(c, 1, lb1)

				txt3 = QLabel()
				txt3.setText('<HTML><p style="color:'+str(self.par_obj.colors[i])+';margin-top:0">t1:</p></HTML>')
				self.win_obj.modelTab.setCellWidget(c, 2, txt3)
				
				

				lb2 = lineEditSp(str(self.x0[i]),self.win_obj,self.par_obj)
				
				lb2.setMaxLength(5)
				lb2.setFixedWidth(30)
			   
				lb2.type = 'tgt1'
				lb2.TGid = i
				self.win_obj.modelTab.setCellWidget(c, 3, lb2)
				
				#self.par_obj.modelTab.setCellWidget(i, 4, photoCrr_btn)
				cbtn = pushButtonSp('Export to fit',self.win_obj,self.par_obj)
			
				cbtn.TGid = i
				self.win_obj.modelTab.setCellWidget(c, 4, cbtn)
				#Make sure the btn knows which list it is connected to.

				#self.par_obj.modelTab.setCellWidget(i, 4, photoCrr_btn)
				sbtn = pushButtonSp3('SaveAs .csv')
			
				sbtn.TGid = i
				sbtn.par_obj = self.par_obj
				sbtn.win_obj = self.win_obj
				sbtn.type = 'sbtn'
				self.win_obj.modelTab.setCellWidget(c, 5, sbtn)
				#Make sure the btn knows which list it is connected to.

				xbtn = pushButtonSp3('X')
				xbtn.setToolTip('Remove data file from software.')
				self.win_obj.modelTab.setCellWidget(c, 6, xbtn)
				xbtn.id = c
				xbtn.par_obj = self.par_obj
				xbtn.win_obj = self.win_obj
				xbtn.parent_id = self
				xbtn.type = 'xbtn'
				c = c+1
				#cbtn.objList = cbx
	def delete_entry(self):
		self.par_obj.TGnumOfRgn
class pushButtonSp3(QPushButton):
	def __init__(self, parent=None):
		QPushButton.__init__(self,parent)
		self.clicked.connect(self.__clicked)
		self.objId = [];
		self.par_obj = [];
		self.win_obj = [];
		self.parent_id = []
		self.xmin = None
		self.xmax = None
		self.id = []
	def __clicked(self):
		if self.type == 'sbtn':
			self.xmin = int(self.win_obj.multiSelect.x0[self.TGid])
			self.xmax = int(self.win_obj.multiSelect.x1[self.TGid])
			if self.xmin >self.xmax:
				xtemp = self.xmax
				self.xmax = self.xmin
				self.xmin = xtemp
			self.win_obj.save_as_specific_csv(self.xmin,self.xmax-1)

		if self.type == 'xbtn':
			self.par_obj.TGnumOfRgn.pop(self.id)
			self.win_obj.modelTab.setRowCount(0)
			#self.win_obj.modelTab.setRowCount(self.par_obj.TGnumOfRgn.__len__())
			self.parent_id.generateList()
		if self.type =='remove_file':
			
			self.par_obj.numOfLoaded = self.par_obj.numOfLoaded - 1
			self.par_obj.objectRef.pop(self.id)
			self.win_obj.modelTab2.setRowCount(0)
			self.win_obj.carpet_browser.modelTab2.setRowCount(0)
			self.parent_id.generateList()
			if self.par_obj.numOfLoaded == 0:
				self.win_obj.plotDataQueueFn()
				self.win_obj.plot_PhotonCount(None)
				self.win_obj.DeltatEdit.setText("")



		

class folderOutput(QMainWindow):
	
	def __init__(self,parent):
		super(folderOutput, self).__init__()
	   
		self.initUI()
		self.parent = parent
		self.parent.config ={}
		
		try:
			filename =	os.path.expanduser('~')+'/FCS_Analysis/config.p'	
			filename.replace('\\', '/')

			self.parent.config = pickle.load(open(filename, "r" ))
			self.filepath = str(self.parent.config['output_corr_filepath'])

		except:
			self.filepath = os.path.expanduser('~')+'/FCS_Analysis/output/'
			try:
				os.makedirs(self.filepath)
			except OSError as exception:
				if exception.errno != errno.EEXIST:
					raise
		
		
	def initUI(self):      

		self.textEdit = QTextEdit()
		self.setCentralWidget(self.textEdit)
		self.statusBar()

		openFile = QAction(QIcon('open.png'), 'Open', self)
		openFile.triggered.connect(self.showDialog)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(openFile)       
		
		self.setGeometry(300, 300, 350, 500)
		self.setWindowTitle('Select a Folder')
		#self.show()
		
	def showDialog(self):

		if self.type == 'output_corr_dir':
			#folderSelect = QFileDialog()
			#folderSelect.setDirectory(self.filepath);
			tfilepath = str(QFileDialog.getExistingDirectory(self, "Select Directory",self.filepath))
			
			if tfilepath !='':
				self.filepath = tfilepath

			#Save to the config file.
				self.parent.config['output_corr_filepath'] = str(tfilepath)
				filename = str(os.path.expanduser('~')+'/FCS_Analysis/config.p')
				filename.replace('\\', '/')
				
				pickle.dump(self.parent.config, open(filename, "wb" ))              


class baseList(QLabel):
	def __init__(self):
		super(baseList, self).__init__()
		self.listId=0
	def mousePressEvent(self,ev):
		pass
class ParameterClass():
	def __init__(self):
		
		#Where the data is stored.
		
		self.objectRef =[]
		self.ax_cb = [];
		self.numOfLoaded = 0
		self.TGnumOfRgn = []
		self.start_pt = 0
		self.end_pt = 0
		self.interval_pt = 1
		self.colors = ['blue','green','red','orange','magenta','midnightblue','black']
		
	


def start_gui():
	app = QApplication(sys.argv)
	#app.setStyle(QStyleFactory.create("GTK+"))

	win_tab = QTabWidget()
	par_obj = ParameterClass()
	fit_obj = Form('scan')
	
	fit_obj.app = app
	
	
	mainWin = Window(par_obj,fit_obj)

	style_sheet_d = """ QPushButton {color: #333;
								border: 1px solid #000000;
								border-radius: 3px;
								padding: 5px;
								background: qradialgradient(cx: 0.3, cy: -0.4,
								fx: 0.3, fy: -0.4,
								radius: 1.9, stop: 0 #fff, stop: 1 #888);
								}

					QPushButton:pressed {
						background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
														  stop: 0 #dadbde, stop: 1 #f6f7fa);
					}

					QPushButton:checked {
						background-color: red;
					}

					QPushButton:flat {
						border: none; /* no border for a flat push button */
					}

					QPushButton:default {
						border-color: navy; /* make the default button prominent */
					}
								
					
								
					QTableView::item:pressed, QListView::item:pressed, QTreeView::item:pressed, 
					QTableView, QHeaderView, QTableView::item:pressed, QListView::item:pressed, QTreeView::item:pressed,
					QHeaderView::section::horizontal::first, QHeaderView::section::horizontal::only-one,
					QTableView::item:selected:active, QTreeView::item:selected:active, QListView::item:selected:active,
					QHeaderView, QHeaderView::section, QHeaderView::section::horizontal::first, 
					QHeaderView::section::vertical::only-one, QTableCornerButton::section
					{Background-color:#dadbde;gridline-color: #dadbde;border-radius: 1px;
					}
					QSplitter::handle:vertical   {height: 6px; image: url(images/vsplitter.png);}
					QSplitter::handle:horizontal {width:  6px; image: url(images/hsplitter.png);}
					QTableView {color: #333;
								border: 1px solid #000000;
								border-radius: 3px;
								padding: 2px;
								background: #dadbde}
	"""
	
	#mainWin.setStyleSheet(style_sheet_d)
	#fit_obj.setStyleSheet(style_sheet_d)
	#win_tab.setStyleSheet(style_sheet_d)
	#app.setStyleSheet(style_sheet_d)



	
	
	#win_tab.setPalette(palette)
	
	win_tab.addTab(mainWin, "Load And Correlate Data")
	win_tab.addTab(fit_obj, "FCS Function Fitting")
	win_tab.setTabToolTip(0,"test1")
	win_tab.setTabToolTip(1,"test2")
	win_tab.resize(1400,800)

	def closeEvent(event):
		try:
			win_obj.carpet_browser.close()
		except:
			pass
		event.accept()
	win_tab.closeEvent = closeEvent

	
	

	
	
	
	

	warnings.filterwarnings('ignore', '.*mages are not supported on non-linear axes.*',)
	warnings.filterwarnings('ignore', '.*aspect is not supported for*',)
	mainWin.app = app
	win_tab.setAttribute(QtCore.Qt.WA_DeleteOnClose)

	
	return win_tab, app,par_obj,mainWin,fit_obj
	
if __name__ == '__main__':
	
	win_tab, app,par_obj,win_obj,fit_obj = start_gui()
	win_obj.testing = False #Is set to true when testing. Sets file  path locations automatically.
	win_tab.show()

	sys.exit(app.exec_())



	

	
