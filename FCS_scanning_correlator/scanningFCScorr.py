from __future__ import division
import numpy as np



import sys,os
from PyQt4 import QtGui, QtCore
import matplotlib
matplotlib.use('Agg') # before import pylab

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec
from matplotlib.widgets import  SpanSelector


import matplotlib.cm as cm

sys.path.append('../../FCS_point/FCS_point_correlator/focuspoint')
from simport_methods import Import_lif, Import_tiff, Import_lsm, Import_msr
from splugin_methods import bleachCorr, ImpAdvWin, bleachCorr2, bleachCorr3, SpotSizeCalculation
from scorrelation_objects import scanObject
from correlation_objects import corrObject

from fitting_gui import Form
import os.path
import warnings
import pickle
import errno
import tifffile as tif_fn
import json
import copy
import uuid
import datetime
now = datetime.datetime.now()

if now.year == 2017:
        print 'trial version expired'
        exit()

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

class FileDialog(QtGui.QMainWindow):
	def __init__(self, win_obj, par_obj, fit_obj):
		super(FileDialog, self).__init__()
	   
		
		self.initUI()
		self.par_obj = par_obj
		self.fit_obj = fit_obj
		self.win_obj = win_obj

		
		
	def initUI(self):      

		self.textEdit = QtGui.QTextEdit()
		self.setCentralWidget(self.textEdit)
		self.statusBar()

		openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
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
		fileInt = QtGui.QFileDialog()
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
		imLif_Arr = []
		self.win_obj.yes_to_all = None
		print 's0',self.win_obj.yes_to_all
		self.win_obj.last_in_list = False
		file_list = fileInt.getOpenFileNames(self, 'Open a data file',self.loadpath, 'lif tif and lsm files (*.lif *.msr *.tif *.tiff *.lsm);;All Files (*.*)')
		c = 1
		for filename in file_list:
			if file_list.__len__() == c:
				self.win_obj.last_in_list = True
			nameAndExt = os.path.basename(str(filename)).split('.')
			fileExt = nameAndExt[-1]
			if fileExt == 'lif':
				imLif = Import_lif(filename,self.par_obj,self.win_obj)
				imLif_Arr.append(imLif)

			if fileExt == 'msr':
				imMsr = Import_msr(filename,self.par_obj,self.win_obj)
			if fileExt == 'tif' or fileExt == 'tiff':
				imTif = Import_tiff(filename,self.par_obj,self.win_obj)
				self.par_obj.objectRef[-1].cb.setChecked(True)
			if fileExt == 'lsm':
				imTif = Import_lsm(filename,self.par_obj,self.win_obj)
			c +=1 
		
		#self.win_obj.yes_to_all = None
		if fileExt == 'lif':
			#We actually import the image file after the list selection to speed the process of selection with multiple files.
			for imLif in imLif_Arr:
				imLif.import_lif_sing(imLif.selList)
				
		self.par_obj.objectRef[-1].cb.setChecked(True)
		self.par_obj.objectRef[-1].plotOn = True
		self.win_obj.DeltatEdit.setText(str(self.par_obj.objectRef[-1].deltat));
			
		try:
			self.loadpath = str(QtCore.QFileInfo(filename).absolutePath())
			filename = os.path.expanduser('~')+'/FCS_Analysis/configLoad'
			filename.replace('\\', '/')

			f = open(filename, 'w')

			f.write(self.loadpath)
			f.close()

		
			
		except:
			pass
		#Sets the first one to be plotted which triggers plotQueueFn
		
		
			

			
		







	
class Window(QtGui.QWidget):
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
		self.bleachCorr1_checked = False
		self.bleachCorr2_checked = False
		# this is the Canvas Widget that displays the `figure`
		

		self.canvas1 = FigureCanvas(self.figure1)
		self.figure1.patch.set_facecolor('white')
		self.canvas1.setStyleSheet("padding-left: 5px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.toolbar1 = NavigationToolbar(self.canvas1, self)
		jar = QtGui.QVBoxLayout()
		jar.addWidget(self.canvas1)

		self.corr_window = QtGui.QGroupBox('Correlation carpet and selected correlation profiles')
		self.corr_window_layout = QtGui.QVBoxLayout()
		self.corr_window.setLayout(self.corr_window_layout)
		
		self.corr_window_layout.setSpacing(0)
		self.corr_window_layout.addLayout(jar)
		

		# this is the Navigation widget
		# it takes the Canvas widget and a parent
		

		self.figure2 = plt.figure()
		self.canvas2 = FigureCanvas(self.figure2)

		self.figure3 = plt.figure()
		self.canvas3 = FigureCanvas(self.figure3)
		
		self.label = scanFileList(self,self.par_obj)
		#self.canvas1.mpl_connect('resize_event',self.figure1.tight_layout())
		#self.canvas2.mpl_connect('resize_event',self.figure2.tight_layout())
		#self.canvas3.mpl_connect('resize_event',self.figure3.tight_layout())
		#self.GateScanFileListObj = GateScanFileList(self, self.par_obj)

		#The table which shows the details of the time-gating.
		self.modelTab = QtGui.QTableWidget(self)
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
		self.modelTab.setHorizontalHeaderLabels(QtCore.QString(",From: , ,To: ,, , , , ").split(","))

		#The table which shows the details of each correlated file. 
		self.modelTab2 = QtGui.QTableWidget()
		self.modelTab2.setRowCount(0)
		self.modelTab2.setColumnCount(6)
		self.modelTab2.setColumnWidth(0,80);
		self.modelTab2.setColumnWidth(1,140);
		self.modelTab2.setColumnWidth(2,30);
		self.modelTab2.setColumnWidth(3,140);
		#self.modelTab2.setColumnWidth(4,100);
		self.modelTab2.setColumnWidth(4,30);
		self.modelTab2.setColumnWidth(5,100);
		self.modelTab2.horizontalHeader().setStretchLastSection(True)
		self.modelTab2.resize(800,400)
		self.modelTab2.setHorizontalHeaderLabels(QtCore.QString(",data name,plot, file name,,file name").split(","))

		
		correlationBtns =  QtGui.QVBoxLayout()
		corrTopRow = QtGui.QHBoxLayout()
		self.corrBotRow = QtGui.QHBoxLayout()
		self.fileDialog = QtGui.QFileDialog()
		self.centre_panel = QtGui.QVBoxLayout()
		self.right_panel = QtGui.QVBoxLayout()
		

		#LEFT PANEL
		self.left_panel = QtGui.QVBoxLayout()
		
		self.left_panel_top = QtGui.QVBoxLayout()
		self.left_panel_top.setSpacing(0)
		
		#Plots of the raw data.
		self.raw_group = QtGui.QGroupBox('Raw data plots')
		self.figure4 = plt.figure(figsize=(2,7))
		self.canvas4 = FigureCanvas(self.figure4)
		self.figure4.patch.set_facecolor('white')
		self.figure5 = plt.figure(figsize=(2,7))
		self.canvas5 = FigureCanvas(self.figure5)
		self.figure5.patch.set_facecolor('white')
		
		self.left_panel.addWidget(self.raw_group)
		self.left_panel_top.addWidget(self.canvas4)
		self.left_panel_top.addWidget(self.canvas5)
		self.raw_group.setLayout(self.left_panel_top)
		
		#LEFT PANEL btns
		self.left_panel_mid_btns= QtGui.QHBoxLayout()
		
		prevPane = QtGui.QPushButton('Prev pane')
		nextPane = QtGui.QPushButton('Next pane')
		prevPane.setStyleSheet("padding-left: 5px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		nextPane.setStyleSheet("padding-left: 5px; padding-right: 3px;padding-top: 1px; padding-bottom: 1px;");
		prevPane.clicked.connect(self.prevPaneFn)
		nextPane.clicked.connect(self.nextPaneFn)


		self.left_panel_mid_btns.addWidget(prevPane)
		self.left_panel_mid_btns.addWidget(nextPane)
		self.left_panel_mid_btns.addStretch()
		self.left_panel_top.addLayout(self.left_panel_mid_btns)


		#LEFT PANEL centre
		self.left_panel_centre = QtGui.QHBoxLayout()
		
		self.left_panel_centre_right = QtGui.QVBoxLayout()
		self.left_panel.addLayout(self.left_panel_centre)
		self.left_panel_centre.addWidget(self.modelTab)
		self.left_panel_centre.addLayout(self.left_panel_centre_right)
		


		#LEFT PANEL centre right
		self.ex = FileDialog(self, par_obj, fit_obj)
		self.openFile = QtGui.QPushButton('Open File')
		self.openFile.clicked.connect(self.ex.showDialog)
		self.spacer = QtGui.QLabel()
		main_layout = QtGui.QHBoxLayout()
		self.import_adv_btn = QtGui.QPushButton('Crop image')
		self.imp_adv_win = ImpAdvWin(self.par_obj,self)
		self.import_adv_btn.clicked.connect(self.imp_adv_win.create_main_frame)
		self.reprocess_btn = QtGui.QPushButton('reprocess data')
		self.reprocess_btn.clicked.connect(self.reprocessDataFn)
		
		
		self.mText = QtGui.QLabel('m (quality):')
		self.mText.resize(50,40)
		self.mEdit =lineEditSp('30',self, self.par_obj)
		self.mEdit.type ='m'
		self.DeltatText = QtGui.QLabel('Deltat (ms):')
		self.DeltatEdit = QtGui.QLabel()
		self.DeltatEdit.par_obj = self
		self.DeltatEdit.type = 'deltat'

		self.spatialBinText = QtGui.QLabel()
		self.spatialBinText.setText('Integrated Bin Size: ')
		self.spatialBinEdit = QtGui.QSpinBox()
		self.spatialBinEdit.setRange(1,51);
		self.spatialBinEdit.setSingleStep(2)
		self.spatialBinEdit.par_obj = self
		self.spatialBinEdit.resize(40,50)


		self.left_panel_centre_right.setSpacing(0)
		self.left_panel_centre_right.addWidget(self.openFile)
		self.left_panel_centre_right.addWidget(self.import_adv_btn)
		self.left_panel_centre_right.addWidget(self.mText)
		self.left_panel_centre_right.addWidget(self.mEdit)
		self.left_panel_centre_right.addWidget(self.DeltatText)
		self.left_panel_centre_right.addWidget(self.DeltatEdit)
		self.left_panel_centre_right.addWidget(self.spatialBinText)
		self.left_panel_centre_right.addWidget(self.spatialBinEdit)
		self.left_panel_centre_right.addWidget(self.reprocess_btn)
		self.left_panel_centre_right.setAlignment(QtCore.Qt.AlignTop)
		



		self.right_panel.addWidget(self.corr_window)
		self.corr_window_layout.addLayout(correlationBtns)
		
		self.right_panel.addWidget(self.modelTab2)

		self.bleachCorr1_btn = QtGui.QPushButton('PBC (Fit)')
		#self.bleachCorr1_btn.setStyleSheet("padding-left: 5px; padding-right: 20px;padding-top: 1px; padding-bottom: 0px;");
		self.bleachCorr1_on_off = QtGui.QPushButton('OFF')
		self.bleachCorr1_on_off.setStyleSheet(" color: red;");
		self.bleachCorr1_on_off.clicked.connect(self.bleachCorr1fn)
		

		self.bleachCorr2_btn = QtGui.QPushButton('PBC (LA)')
		#self.bleachCorr2_btn.setStyleSheet("padding-left: 5px; padding-right: 15px;padding-top: 1px; padding-bottom: 0px;");
		self.bleachCorr2_on_off = QtGui.QPushButton('OFF')
		self.bleachCorr2_on_off.setStyleSheet(" color: red;");
		self.bleachCorr2_on_off.clicked.connect(self.bleachCorr2fn)
		#self.bleachCorr2_on_off.setEnabled(False);

		
		self.displayCarpetText = QtGui.QLabel('Display:')
		self.displayCarpetText.setMinimumHeight(12)
		self.displayCarpetText.setMaximumHeight(12)
		#self.displayCarpetText.setStyleSheet("border-radius:0px;padding-left: 10px; padding-right: 5px;padding-top 5px;");
		self.CH0Auto_btn = QtGui.QPushButton('Auto CH0')
		self.CH0Auto_btn.setStyleSheet("color: green;");
		self.CH1Auto_btn = QtGui.QPushButton('Auto CH1')
		#self.CH1Auto_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 0px;");
		self.CH01Cross_btn = QtGui.QPushButton('Cross CH01')
		self.displayExportText = QtGui.QLabel('Export:')
		self.displayExportText.setMinimumHeight(12)
		self.displayExportText.setMaximumHeight(12)

		#self.displayExportText.setStyleSheet("padding-left: 10px; padding-right: 5px;padding-top: 5px; ");
		self.export_region_btn = QtGui.QPushButton('Export to Fit');
		#self.CH01Cross_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 0px;");
		self.addRegion_btn = QtGui.QPushButton('Store Region');
		#self.addRegion_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 0px;");
		self.export_region_btn = QtGui.QPushButton('Export to Fit');
		#self.export_region_btn.setStyleSheet("padding-left: 10px; padding-right: 10px;padding-top: 1px; padding-bottom: 0px;");
		
		self.CH0Auto_btn.clicked.connect(self.CH0AutoFn)
		self.CH1Auto_btn.clicked.connect(self.CH1AutoFn)
		self.CH01Cross_btn.clicked.connect(self.CH01CrossFn)
		self.export_region_btn.clicked.connect(self.export_track_to_fit)
		self.TGScrollBoxObj = GateScanFileList(self,self.par_obj)
		self.bleachInt = bleachCorr(self.par_obj,self)
		self.bleachInt2 = bleachCorr2(self.par_obj,self)
		self.bleachCorr1_btn.clicked.connect(self.bleachInt.create_main_frame)
		self.bleachCorr2_btn.clicked.connect(self.bleachInt2.create_main_frame)
		self.addRegion_btn.clicked.connect(self.saveRegion)
		
		
		corrTopRow.setSpacing(0)
		corrTopRow.addWidget(self.bleachCorr1_btn)
		corrTopRow.addWidget(self.bleachCorr1_on_off)
		corrTopRow.addWidget(self.bleachCorr2_btn)
		corrTopRow.addWidget(self.bleachCorr2_on_off)
		corrTopRow.addWidget(self.displayCarpetText)
		corrTopRow.addWidget(self.CH0Auto_btn)
		corrTopRow.addWidget(self.CH1Auto_btn)
		corrTopRow.addWidget(self.CH01Cross_btn)
		corrTopRow.addWidget(self.displayExportText)
		corrTopRow.addWidget(self.addRegion_btn)
		corrTopRow.addWidget(self.export_region_btn)



		self.folderOutput = folderOutput(self)
		self.folderOutput.type = 'output_corr_dir'

		self.folderSelect_btn = QtGui.QPushButton('Set Output Folder')
		#self.folderSelect_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)
		
	
		self.save_corr_txt = QtGui.QLabel('Save:')
		#self.save_corr_txt.setStyleSheet("spacing: 0px;padding-left: 10px; padding-right:2px;padding-top: 0px; padding-bottom: 0px;");
		self.save_corr_txt.setMinimumHeight(12)
		self.save_corr_txt.setMaximumHeight(12)
		self.save_corr_carpet_btn = QtGui.QPushButton('Raw Carpet')
		#self.save_corr_carpet_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.save_corr_carpet_btn.clicked.connect(self.save_carpets)

		self.save_log_corr_carpet_btn = QtGui.QPushButton('Log Norm. Carpet')
		#self.save_log_corr_carpet_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.save_log_corr_carpet_btn.clicked.connect(self.save_log_carpets)

		self.save_figure_btn = QtGui.QPushButton('Figure')
		#self.save_figure_btn.setStyleSheet("padding-left: 10px; padding-right: 20px;padding-top: 1px; padding-bottom: 1px;");
		self.save_figure_btn.clicked.connect(self.save_figure)

		self.spot_size_calc = QtGui.QPushButton('Calc. Spot Size')

		self.spot_size_calc_plugin = SpotSizeCalculation(self.par_obj,self)
		self.spot_size_calc.clicked.connect(self.spot_size_calc_plugin.create_main_frame)

		

		self.corrBotRow.setSpacing(0)
		self.corrBotRow.addWidget(self.folderSelect_btn)
		self.corrBotRow.addWidget(self.save_corr_txt )
		self.corrBotRow.addWidget(self.save_corr_carpet_btn)
		self.corrBotRow.addWidget(self.save_log_corr_carpet_btn)
		self.corrBotRow.addWidget(self.save_figure_btn)
		self.corrBotRow.addWidget(self.spot_size_calc)
		self.corrBotRow.addStretch()
		self.corrBotRow.addWidget(self.toolbar1)
		
		
		panel_third_row_btns = QtGui.QHBoxLayout()

		export_all_data_btn = QtGui.QPushButton('Export All Data to Fit')
		export_all_data_btn.clicked.connect(self.export_all_data_fn)
		export_all_data_to_csv_btn = QtGui.QPushButton('Export All Data to csv')
		export_all_data_to_csv_btn.clicked.connect(self.save_all_as_csv_fn)
		
		panel_third_row_btns.addWidget(export_all_data_btn)
		panel_third_row_btns.addWidget(export_all_data_to_csv_btn)
		panel_third_row_btns.addStretch()
		
		self.corr_window_layout.setSpacing(0)
		self.corr_window_layout.addStretch()
		
		self.image_status_text = QtGui.QStatusBar()
		
		self.image_status_text.showMessage("Please load a data file. ")
		self.image_status_text.setStyleSheet("QLabel {  color : green }")
		
		
		self.setLayout(main_layout)
		main_layout.addLayout(self.left_panel)
		
		correlationBtns.addLayout(corrTopRow)
		correlationBtns.addLayout(self.corrBotRow)
		correlationBtns.addLayout(panel_third_row_btns)
		correlationBtns.setSpacing(0)
		main_layout.addLayout(self.right_panel)
		
		
		

		self.left_panel.addWidget(self.image_status_text)
		#Advanced grid structure for the plot windows.
		gs = gridspec.GridSpec(2, 3, height_ratios=[1, 0.98],width_ratios=[0.02, 0.96,0.02]) 
		#Main correlation window
		self.plt1 = self.figure1.add_subplot(gs[0,:])
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

		
		self.multiSelect = GateScanFileList(self,self.par_obj)

		self.update_correlation_parameters()
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
				if objId.bleachCorr1 == True:
					if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
						#The bleach correction is on now we turn it off.
						self.bleachCorr1_on_off.setText('OFF')
						self.bleachCorr1_on_off.setStyleSheet("color: red");
						self.bleachCorr1_checked = False
						self.plotDataQueueFn()
					else:
						#The bleach correction is off now we turn it on.
						self.bleachCorr1_on_off.setText('ON')
						self.bleachCorr1_on_off.setStyleSheet("color: green");
						self.bleachCorr1_checked = True
						self.plotDataQueueFn()
				
						
						

		
	def bleachCorr2fn(self):
		for objId in self.par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				if objId.bleachCorr2 == True:
					if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
						#The bleach correction is on now we turn it off.
						self.bleachCorr2_on_off.setText('OFF')
						self.bleachCorr2_on_off.setStyleSheet("color: red");
						self.bleachCorr2_checked = False
						self.plotDataQueueFn()
					else:
						#The bleach correction is off now we turn it on.
						self.bleachCorr2_on_off.setText('ON')
						self.bleachCorr2_on_off.setStyleSheet("color: green");
						self.bleachCorr2_checked = True
						self.plotDataQueueFn()
				
						

						
					
		


	def update_correlation_parameters(self):
		""""""
		self.par_obj.spatialBin = int(self.spatialBinEdit.value())
		self.par_obj.m = float(self.mEdit.text())
		
	def CH0AutoFn(self):
		"""We change the view of the carpetDisplay to the auto-correlation channel 0. """
		self.carpetDisplay = 0
		self.CH0Auto_btn.setStyleSheet(" color: green")
		self.CH1Auto_btn.setStyleSheet(" color: black")
		self.CH01Cross_btn.setStyleSheet(" color: black")
		self.plotDataQueueFn()

	def CH1AutoFn(self):
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
						export_im[1,:,:] = objId.AutoCorr_carpetCH0_pc[:,:].T;
					else:
						export_im =np.zeros((height,width))
						export_im[:,:] = objId.AutoCorr_carpetCH0[:,:].T;

				if objId.numOfCH ==2:
					if objId.bleachCorr1 == True or objId.bleachCorr2 == True:
						export_im =np.zeros((4,height,width))
						export_im[0,:,:] = objId.AutoCorr_carpetCH0[:,:].T;
						export_im[1,:,:] = objId.AutoCorr_carpetCH0_pc[:,:].T;
						export_im[2,:,:] = objId.AutoCorr_carpetCH1[:,:].T;
						export_im[3,:,:] = objId.AutoCorr_carpetCH1_pc[:,:].T;
					else:
						export_im =np.zeros((2,height,width))
						export_im[0,:,:] = objId.AutoCorr_carpetCH0[:,:].T;
						export_im[1,:,:] = objId.AutoCorr_carpetCH1[:,:].T;

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
		
	def prevPaneFn(self):
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
	def nextPaneFn(self):
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
		self.update_correlation_parameters()
		for objId in self.par_obj.objectRef:
					objId.processData()
					objId.bleachCorr1 = False
					objId.bleachCorr2 = False


		self.bleachCorr2_checked = False
		self.bleachCorr1_checked = False
		self.bleachCorr1_on_off.setText('OFF')
		self.bleachCorr1_on_off.setStyleSheet(" color: red");
		self.bleachCorr2_on_off.setText('OFF')
		self.bleachCorr2_on_off.setStyleSheet(" color: red");
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
		
		#self.plt1.set_ylim(bottom=0)
		#self.plt5.ax = plt.gca()
		#self.plt5.a.freshDraw()
	def plot_PhotonCount(self,objId):
		"""Plots the photon counting"""
		
		self.plt4.clear()
		self.canvas4.draw()

		
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
				totalFn = objId.CH0[:,xmin]
			else:
				totalFn = np.sum(objId.CH0[:,xmin:xmax], 1).astype(np.float64)
			
			self.plt4.plot(np.arange(0,totalFn.shape[0],10)*objId.deltat ,totalFn[0::10],color=objId.color)
			
			if objId.numOfCH == 2:
				#If just one line is highlighted.
				if xmin == xmax:
					totalFn = objId.CH1[:,xmin]
				else:
					totalFn = np.sum(objId.CH1[:,xmin:xmax], 1).astype(np.float64)
				
				self.plt4.plot(np.arange(0,totalFn.shape[0],10)*objId.deltat ,totalFn[0::10],'grey')
		
		if self.int_time_trace_mode == 'first_pane':
			yLimMn = int(((objId.pane)*(objId.CH0.shape[1]/64)*150))
			yLimMx = int(((objId.pane+1)*(objId.CH0.shape[1]/64)*150))
			
			#If just one line is highlighted.
			if xmin == xmax:
				totalFn = objId.CH0[:,xmin]
			else:
				totalFn = np.sum(objId.CH0[:,xmin:xmax], 1).astype(np.float64)
			self.plt4.plot(np.arange(yLimMn,yLimMx)*objId.deltat ,totalFn[yLimMn:yLimMx],color=objId.color)
			#If two channels are present
			if objId.numOfCH == 2:
				if xmin == xmax:
					totalFn = objId.CH1[:,xmin]
				else:
					totalFn = np.sum(objId.CH1[:,xmin:xmax], 1).astype(np.float64)
				self.plt4.plot(np.arange(yLimMn,yLimMx)*objId.deltat ,totalFn[yLimMn:yLimMx],color='grey')


		self.figure4.subplots_adjust(bottom=0.15,right=0.95)
		self.plt4.tick_params(axis='both', which='major', labelsize=8)
		#self.figure4.tight_layout(pad=1.08)

		self.plt4.set_xlabel('Time (ms) ', fontsize=8)
		self.plt4.set_ylabel('Intensity Counts (CH0 (blue), CH1 (grey))', fontsize=8)
		self.plt4.xaxis.grid(True,'minor')
		self.plt4.xaxis.grid(True,'major')
		self.plt4.yaxis.grid(True,'minor')
		self.plt4.yaxis.grid(True,'major')
		self.plt4.set_autoscale_on(False)
		self.canvas4.draw()

			
	def plot(self,objId):
		''' plots correlation functions '''

		self.autotime = objId.autotime
		auto = objId.autoNorm
		corrText = 'Auto-correlation'
		
		#Where the selected pixel correlation functions are plotted as 2D.
		self.plt1.plot(self.autotime,auto[:,0,0],objId.color)
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
		

		#This is for the raw intensity trace of the data (XT carpet).
		if objId.numOfCH == 1:
			XTcarpet=np.flipud(objId.CH0[yLimMn:yLimMx,:].T)
		elif objId.numOfCH == 2:
			XTcarpet = np.zeros((objId.CH0.shape[1],yLimMx-yLimMn,3))
			XTcarpet[:,:,0]=np.flipud(objId.CH0[yLimMn:yLimMx,:].T)
			XTcarpet[:,:,1]=np.flipud(objId.CH1[yLimMn:yLimMx,:].T)
		
		self.plt5.imshow(((XTcarpet)/np.max(XTcarpet)),interpolation = 'nearest',extent=[yLimMn,yLimMx,0,objId.CH0.shape[1]])
	   
		self.figure5.subplots_adjust(bottom =0.2,left=0.1,right=0.95)
		self.plt5.set_xlabel('Scan line', fontsize=8)
		self.plt5.set_ylabel('Column pixels', fontsize=12)
		self.plt5.tick_params(axis='both', which='major', labelsize=8)
		self.plt5.autoscale(False)
		self.canvas5.draw()


		
		#Checks which channel is displayed and then loads the relevant carpet.
		if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
			
			#This is for the photo-corrected version of the carpets.
			if self.carpetDisplay == 0:
				img = np.flipud(objId.AutoCorr_carpetCH0_pc[:,:].T);
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale_pc
			if self.carpetDisplay == 1:
				img = np.flipud(objId.AutoCorr_carpetCH1_pc[:,:].T);
				sum_img = np.flipud(objId.CH1_arrayColSum)
				carp_scale = objId.corrArrScale_pc
			if self.carpetDisplay == 2:
				img = np.flipud(objId.CrossCorr_carpet01_pc[:,:].T);
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale_pc
		else:
			if self.carpetDisplay == 0:
				img = np.flipud(objId.AutoCorr_carpetCH0[:,:].T);
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale
			if self.carpetDisplay == 1:
				img = np.flipud(objId.AutoCorr_carpetCH1[:,:].T);
				sum_img = np.flipud(objId.CH1_arrayColSum)
				carp_scale = objId.corrArrScale
			if self.carpetDisplay == 2:
				img = np.flipud(objId.CrossCorr_carpet01[:,:].T);
				sum_img = np.flipud(objId.CH0_arrayColSum)
				carp_scale = objId.corrArrScale


		
		
		#The correlation carpet has a logarithmic scale:
		c = np.logspace(np.log10(carp_scale[0]), np.log10(carp_scale[-1]), img.shape[1], endpoint=True)
		e =[]
		for i in range(0,img.shape[1]):
			e.append(min(enumerate(carp_scale), key=lambda x:abs(x[1]-c[i]))[0])

		self.carpet_img = np.zeros(img.shape)
		self.carpet_img = img[:,e]

		self.carpet_img[self.carpet_img < 0]=0;
		for i in range(0, img.shape[0]):
			
			self.carpet_img[i,:] = self.carpet_img[i,:]/np.max(self.carpet_img[i,:])


		self.plt2.set_xlabel('Time (ms)', fontsize=12)
		self.plt2.set_xscale('log')
		self.corr_carpet = self.plt2.imshow(self.carpet_img, extent=[carp_scale[0],carp_scale[-1],0,img.shape[0]],interpolation ='nearest')
		
		

		#Plot the intensity profile to the left.
		im1 = self.plt3.imshow(sum_img.reshape(objId.CH0_arrayColSum.shape[0],1),extent=[0,5,0,img.shape[0]],interpolation = 'nearest',aspect='auto',cmap=cm.Reds_r);
		self.plt3.set_ylabel('Column pixels')
		self.plt3.set_xlabel('Intensity\nmaxima')
		self.plt3.set_xticklabels('')

		
		
		self.canvas1.draw()
		self.plt1.cla()
		
		
		colbar = self.figure1.colorbar(self.corr_carpet, cax=self.plt6)
		colbar.set_label('Scale (normalised to column max)')
		
		self.span2 = SpanSelector(self.plt2, self.onselect, 'vertical', useblit=True, minspan =0, rectprops=dict(edgecolor='black',alpha=1.0, facecolor='None') )
		if self.clickedS1 and self.clickedS2 != None:
			self.onselect(self.clickedS1, self.clickedS2)
			self.plt2.set_ylim([0,img.shape[0]])
		
		if self.clim_low != 0 and self.clim_high != None:
			self.corr_carpetset_clim((0,np.max(imgN)))
		
		self.figure1.subplots_adjust(left=0.1,right=0.90)
		self.plt2.autoscale(False)
		
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
		
		
		cmin  = np.min(self.carpet_img[:,cmin_ind])
		cmax  = np.max(self.carpet_img[:,cmax_ind])
		

		self.corr_carpet.set_clim((cmin,cmax))
		self.canvas1.draw()
		
	def saveRegion(self):
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
			if self.x1 > self.carpet_img.shape[0]:
				self.x1 = int(np.floor(self.carpet_img.shape[0]/2)+0.5)
				self.x0 = int(np.floor(self.carpet_img.shape[0]/2)-0.5)

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
						if self.clickedS1 != None  and self.clickedS2 != None:
							for b in range(self.clickedS1,self.clickedS2):
								self.plt1.set_autoscale_on(True)
								#Is the button checked.
								if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
									if self.carpetDisplay == 0:
										self.plt1.plot(objId.corrArrScale_pc, objId.AutoCorr_carpetCH0_pc[:,int(b)],objId.color)
									if self.carpetDisplay == 1:
										self.plt1.plot(objId.corrArrScale_pc, objId.AutoCorr_carpetCH1_pc[:,int(b)],objId.color)
									if self.carpetDisplay == 2:
										self.plt1.plot(objId.corrArrScale_pc, objId.CrossCorr_carpet01_pc[:,int(b)],objId.color)
								else:
									if self.carpetDisplay == 0:
										self.plt1.plot(objId.corrArrScale ,objId.AutoCorr_carpetCH0[:,int(b)],objId.color)
									if self.carpetDisplay == 1:
										self.plt1.plot(objId.corrArrScale ,objId.AutoCorr_carpetCH1[:,int(b)],objId.color)
									if self.carpetDisplay == 2:
										self.plt1.plot(objId.corrArrScale ,objId.CrossCorr_carpet01[:,int(b)],objId.color)
								
								a,c = self.plt1.get_ylim()
								self.plt1.set_ylim(bottom=0,top=c)
							self.canvas1.draw()
				#self.draw_line()
	def export_track_to_fit(self):

		
		self.export_track_fn()
	def save_as_specific_csv(self,xmin,xmax):
		for objId in self.par_obj.objectRef:
			
			if(objId.cb.isChecked() == True):
				self.save_as_csv(objId,xmin,xmax)
	def save_all_as_csv_fn(self):
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
						
						if self.bleachCorr1_checked == True:
							f.write('pc, 1\n');
							f.write('pbc_f0,'+str(objId.pbc_f0_ch0)+'\n');
							f.write('pbc_tb,'+str(objId.pbc_tb_ch0)+'\n');
							f.write('kcount,'+str(objId.kcountCH0_pc[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+'\n')
						
						if self.bleachCorr2_checked == True:
							f.write('pc, 2\n');
							f.write('kcount,'+str(objId.kcountCH0_pc[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+'\n')
						
						
						if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
							f.write('Time (ns), CH0 Auto-Correlation\n')
							for x in range(0,objId.corrArrScale_pc.shape[0]):
								f.write(str(float(objId.corrArrScale_pc[x]))+','+str(objId.AutoCorr_carpetCH0_pc[x,i])+ '\n')
						else:
							f.write('pc, 0\n');
							f.write('kcount,'+str(objId.kcountCH0[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0[i])+'\n')
							f.write('Time (ns), CH0 Auto-Correlation\n')
							for x in range(0,objId.corrArrScale.shape[0]):
								f.write(str(float(objId.corrArrScale[x]))+','+str(objId.AutoCorr_carpetCH0[x,i])+ '\n')
						f.write('end\n')
						
					if objId.numOfCH == 2:
						f.write('ch_type, 0 ,1, 2\n')
						
						f.write('carpet pos,'+str(i)+'\n')
						f.write('parent_name,'+str(parent_name)+'\n')
						f.write('parent_uqid,'+str(parent_uqid)+'\n')
						f.write('parent_filename,'+str(objId.file_name)+'\n')

						if self.bleachCorr1_checked == True:
							f.write('pc, 1\n');
							f.write('pbc_f0,'+str(objId.pbc_f0_ch0)+','+str(objId.pbc_f0_ch1)+'\n');
							f.write('pbc_tb,'+str(objId.pbc_tb_ch0)+','+str(objId.pbc_tb_ch1)+'\n');
							f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+','+str(objId.numberNandBCH1_pc[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+','+str(objId.brightnessNandBCH1_pc[i])+'\n')
							f.write('CV,'+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+'\n')

						if self.bleachCorr2_checked == True:
							f.write('pc, 2\n');
							f.write('kcount,'+str(objId.kcountCH0_pc[i])+','+str(objId.kcountCH1_pc[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0_pc[i])+','+str(objId.numberNandBCH1_pc[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0_pc[i])+','+str(objId.brightnessNandBCH1_pc[i])+'\n')
							f.write('CV,'+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+','+str(objId.CV_pc[i])+'\n')
						if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
							f.write('Time (ns), CH0 Auto-Correlation, CH1 Auto-Correlation, CH01 Cross-Correlation\n')
							for x in range(0,objId.corrArrScale_pc.shape[0]):
								f.write(str(float(objId.corrArrScale_pc[x]))+','+str(objId.AutoCorr_carpetCH0_pc[x,i])+','+str(objId.AutoCorr_carpetCH1_pc[x,i])+','+str(objId.CrossCorr_carpet01_pc[x,i])+ '\n')
						else:
							f.write('pc, 0\n');
							f.write('kcount,'+str(objId.kcountCH0[i])+','+str(objId.kcountCH1[i])+'\n')
							f.write('numberNandB,'+str(objId.numberNandBCH0[i])+','+str(objId.numberNandBCH1[i])+'\n')
							f.write('brightnessNandB,'+str(objId.brightnessNandBCH0[i])+','+str(objId.brightnessNandBCH1[i])+'\n')
							f.write('CV,'+str(objId.CV[i])+','+str(objId.CV[i])+','+str(objId.CV[i])+'\n')
							f.write('Time (ns), CH0 Auto-Correlation, CH1 Auto-Correlation, CH01 Cross-Correlation\n')
							for x in range(0,objId.corrArrScale.shape[0]):
								f.write(str(float(objId.corrArrScale[x]))+','+str(objId.AutoCorr_carpetCH0[x,i])+','+str(objId.AutoCorr_carpetCH1[x,i])+','+str(objId.CrossCorr_carpet01[x,i])+'\n')
						f.write('end\n')
					f.close()
						






		
		# if self.objId.numOfCH == 2:
		# 	f = open(self.win_obj.folderOutput.filepath+'/'+self.objId.name+'_correlation.csv', 'w')
		# 	f.write('# Time (ns),CH0 Auto-Correlation, CH1 Auto-Correlation, CC01 Auto-Correlation, CC10 Auto-Correlation\n')
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

			if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
				corrObj1.kcount = objId.kcountCH0_pc[i]
				corrObj1.numberNandB = objId.numberNandBCH0_pc[i]
				corrObj1.brightnessNandB = objId.brightnessNandBCH0_pc[i]
				corrObj1.name = objId.name+'row_'+str(i)+'_CH0_Auto_Corr_pc'
				corrObj1.autotime = objId.corrArrScale_pc[:]
				corrObj1.autoNorm = objId.AutoCorr_carpetCH0_pc[:,i]
				if self.bleachCorr1_checked == True:
					#Additional parameters from photobleaching method 1
					corrObj1.pbc_f0 = objId.pbc_f0_ch0
					corrObj1.pbc_tb = objId.pbc_tb_ch0
			else:
				corrObj1.kcount = objId.kcountCH0[i]
				corrObj1.numberNandB = objId.numberNandBCH0[i]
				corrObj1.brightnessNandB = objId.brightnessNandBCH0[i]
				corrObj1.name = objId.name+'row_'+str(i)+'_CH0_Auto_Corr'
				corrObj1.autotime = objId.corrArrScale[:]
				corrObj1.autoNorm = objId.AutoCorr_carpetCH0[:,i]
			
			
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
				
				
				corrObj1.CV = objId.CV[i]
				corrObj2.CV = objId.CV[i]
				corrObj2.type = "scan"
				if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
					corrObj2.kcount = objId.kcountCH1_pc[i]
					corrObj2.numberNandB = objId.numberNandBCH1_pc[i]
					corrObj2.brightnessNandB = objId.brightnessNandBCH1_pc[i]
					corrObj2.name = objId.name+'row_'+str(i)+'_CH1_Auto_Corr_pc'
					corrObj2.autotime =	objId.corrArrScale_pc
					corrObj2.autoNorm = objId.AutoCorr_carpetCH1_pc[:,i]
					if self.bleachCorr1_checked == True:
						#Additional parameters from photobleaching method 1
						corrObj2.pbc_f0 = objId.pbc_f0_ch1
						corrObj2.pbc_tb = objId.pbc_tb_ch1
				else:
					corrObj2.kcount = objId.kcountCH1[i]
					corrObj2.numberNandB = objId.numberNandBCH1[i]
					corrObj2.brightnessNandB = objId.brightnessNandBCH1[i]
					corrObj2.name = objId.name+'row_'+str(i)+'_CH1_Auto_Corr'
					corrObj2.autoNorm = objId.AutoCorr_carpetCH1[:,i]
				
				

				corrObj3 = corrObject(objId.filepath,self.fit_obj);
				corrObj3.siblings = None
				corrObj3.parent_name = parent_name
				corrObj3.parent_uqid = parent_uqid
				corrObj3.file_name = objId.file_name
				self.fit_obj.objIdArr.append(corrObj3.objId)
				
				corrObj3.ch_type = 2
				corrObj3.param = copy.deepcopy(self.fit_obj.def_param)
				corrObj3.CV = objId.CV[i]
				corrObj3.prepare_for_fit()
				corrObj3.autotime = objId.corrArrScale[:]
				if self.bleachCorr1_checked == True or self.bleachCorr2_checked == True:
					corrObj3.name = objId.name+'row_'+str(i)+'_CH01_Auto_Corr_pc'
					corrObj3.autotime =	objId.corrArrScale_pc
					corrObj3.autoNorm = objId.CrossCorr_carpet01_pc[:,i]
				else:
					corrObj3.name = objId.name+'row_'+str(i)+'_CH01_Auto_Corr'
					corrObj3.autoNorm = objId.CrossCorr_carpet01[:,i]
				corrObj3.param = copy.deepcopy(self.fit_obj.def_param)

				corrObj1.siblings = [corrObj2,corrObj3]
				corrObj2.siblings = [corrObj1,corrObj3]
				corrObj3.siblings = [corrObj1,corrObj2]

		self.fit_obj.fill_series_list()


		


class lineEditSp(QtGui.QLineEdit):
	def __init__(self,text,win_obj,par_obj):
		QtGui.QLineEdit.__init__(self,text)
		self.editingFinished.connect(self.__handleEditingFinished)
		self.par_obj = par_obj
		self.win_obj = win_obj
		self.obj = []
		self.type = []
		self.TGid =[]
	def __handleEditingFinished(self):
		self.par_obj.m = float(self.text())
		
		if(self.type == 'tgt0' ):
			
			self.win_obj.multiSelect.x1[self.TGid] = float(self.text())
			
			
			
			
			#plotDataQueueFn()
		if(self.type == 'tgt1' ):
			self.win_obj.multiSelect.x0[self.TGid] = float(self.text())
		   
			
			
			
		if(self.type == 'name' ):
			self.obj.name = str(self.text())

		   
			
	  


			


class pushButtonSp(QtGui.QPushButton):
	def __init__(self,text, win_obj,par_obj):
		QtGui.QComboBox.__init__(self,text)
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
		

						
class checkBoxSp3(QtGui.QCheckBox):
	def __init__(self, par_obj, win_obj):
		QtGui.QCheckBox.__init__(self)
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
			
			#The 
			if self.obj.bleachCorr2 == False:
				self.win_obj.bleachCorr2_on_off.setText('OFF')
				self.win_obj.bleachCorr2_on_off.setStyleSheet("color: red");
				self.win_obj.bleachCorr2_checked = False

			if self.obj.bleachCorr1 == False:
				self.win_obj.bleachCorr1_on_off.setText('OFF')
				self.win_obj.bleachCorr1_on_off.setStyleSheet("color: red");
				self.win_obj.bleachCorr1_checked = False
			
			
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
		
		for i in range(0,self.par_obj.numOfLoaded):
			self.win_obj.modelTab2.setRowCount(i+1)
			#Represents each y
			self._l=QtGui.QHBoxLayout()
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
			lb2 = QtGui.QLabel()
			lb2.setText(self.par_obj.objectRef[i].file_name);
			self.win_obj.modelTab2.setCellWidget(i, 3, lb2)

			
			#Adds save button to the file.
			#sb = pushButtonSp2('save file')
			#sb.par_obj = self.par_obj
			#sb.win_obj = self.win_obj
			#sb.objId = self.par_obj.objectRef[i]
			#self.win_obj.modelTab2.setCellWidget(i, 4, sb)

			#Adds save button to the file.
			xb = pushButtonSp3('X')
			xb.par_obj = self.par_obj
			xb.win_obj = self.win_obj
			xb.id = i
			xb.type = 'remove_file'
			xb.parent_id = self
			self.win_obj.modelTab2.setCellWidget(i, 4, xb)


			#The filename
			b = baseList()
			b.setText('<HTML><p style="margin-top:0">'+self.par_obj.objectRef[i].ext+' file :'+str(self.par_obj.data[i])+' </p></HTML>')
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
				
				txt2 = QtGui.QLabel()
				txt2.setText('<HTML><p style="color:'+str(self.par_obj.colors[i])+';margin-top:0">t0:</p></HTML>')
				self.win_obj.modelTab.setCellWidget(c, 0, txt2)


				lb1 = lineEditSp(str(self.x1[i]),self.win_obj,self.par_obj)
				lb1.setMaxLength(5)
				lb1.setFixedWidth(30)
				lb1.setText(str(self.x1[i]))
				lb1.type = 'tgt0'
				lb1.TGid = i
				self.win_obj.modelTab.setCellWidget(c, 1, lb1)

				txt3 = QtGui.QLabel()
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
class pushButtonSp3(QtGui.QPushButton):
	def __init__(self, parent=None):
		QtGui.QPushButton.__init__(self,parent)
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
			self.parent_id.generateList()



		

class folderOutput(QtGui.QMainWindow):
	
	def __init__(self,parent):
		super(folderOutput, self).__init__()
	   
		self.initUI()
		self.parent = parent
		self.parent.config ={}
		
		try:
			filename =	os.path.expanduser('~')+'/FCS_Analysis/config.p'	
			filename.replace('\\', '/')

			self.parent.config = pickle.load(open(filename, "rb" ));
			self.filepath = self.parent.config['output_corr_filepath']
		except:
			self.filepath = os.path.expanduser('~')+'/FCS_Analysis/output/'
			try:
				os.makedirs(self.filepath)
			except OSError as exception:
				if exception.errno != errno.EEXIST:
					raise
		
		
	def initUI(self):      

		self.textEdit = QtGui.QTextEdit()
		self.setCentralWidget(self.textEdit)
		self.statusBar()

		openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
		openFile.triggered.connect(self.showDialog)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(openFile)       
		
		self.setGeometry(300, 300, 350, 500)
		self.setWindowTitle('Select a Folder')
		#self.show()
		
	def showDialog(self):

		if self.type == 'output_corr_dir':
			#folderSelect = QtGui.QFileDialog()
			#folderSelect.setDirectory(self.filepath);
			tfilepath = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory",self.filepath))
			
			if tfilepath !='':
				self.filepath = tfilepath
			#Save to the config file.
				self.parent.config['output_corr_filepath'] = str(tfilepath)
				filename = str(os.path.expanduser('~')+'/FCS_Analysis/config.p')
				filename.replace('\\', '/')
				pickle.dump(self.parent.config, open(filename, "w" ))              


class baseList(QtGui.QLabel):
	def __init__(self):
		super(baseList, self).__init__()
		self.listId=0
	def mousePressEvent(self,ev):
		pass
class ParameterClass():
	def __init__(self):
		
		#Where the data is stored.
		self.data = []
		self.objectRef =[]
		self.data = []
		self.ax_cb = [];
		self.numOfLoaded = 0
		self.TGnumOfRgn = []
		self.start_pt = 0
		self.end_pt = 0
		self.interval_pt = 1
		self.colors = ['blue','green','red','cyan','magenta','midnightblue','black']
		self.gui  ='show'
	
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	#app.setStyle(QtGui.QStyleFactory.create("GTK+"))

	win_tab = QtGui.QTabWidget()
	par_obj = ParameterClass()
	fit_obj = Form('scan')
	
	fit_obj.app = app
	
	
	mainWin = Window(par_obj,fit_obj)
	
	win_tab.addTab(mainWin, "Load scanning data")
	win_tab.addTab(fit_obj, "Fit Function")
	win_tab.resize(1200,800)
	

	
	#path = '/Users/dwaithe/Documents/collaborators/EggelingC/data/Scanning FCS data/from Jorge/'
	#filename = '20140902_ScanFCCS_Jcam Glass LCksnap STAR Sri.lif'
	#par_obj.gui  ='show'
	#filepath = path+filename
	#scanlist = Import_lif(filepath,par_obj, mainWin)
	#c=0
	#selList =[];
	#for name in scanlist.store:
#		c = c+1

		#exec("boolV = self.check"+str(c)+".isChecked()");
#		if c == 3:
#			selList.append(name)
#	print selList.__len__()
#	scanlist.import_lif_sing(selList)
#	mainWin.testWin.close()
#	mainWin.plotDataQueueFn()
	
	
	

	warnings.filterwarnings('ignore', '.*mages are not supported on non-linear axes.*',)
	warnings.filterwarnings('ignore', '.*aspect is not supported for*',)
	
	

	
	
	win_tab.show()



	sys.exit(app.exec_())

	
