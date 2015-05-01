from __future__ import division
import numpy as np



import sys,os
from PyQt4 import QtGui, QtCore
import matplotlib
matplotlib.use('Agg') # before import pylab

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec


import matplotlib.cm as cm

sys.path.append('../../FCS_point/FCS_point_correlator')
from simport_methods import Import_lif, Import_tiff, Import_lsm
from splugin_methods import bleachCorr, ImpAdvWin
from scorrelation_objects import corrObject

from fitting_gui import Form
import os.path

import pickle
import errno
import tifffile as tif_fn
import json
import copy

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
            f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'r')
            self.loadpath =f.readline()
            f.close() 
        except:
            #If not default will do.
            self.loadpath = os.path.expanduser('~')+'/FCS_Analysis/'

        #Create loop which opens dialog box and allows selection of files.
        for filename in fileInt.getOpenFileNames(self, 'Open a data file',self.loadpath, 'lif files (*.lif);;All Files (*.*)'):
            nameAndExt = os.path.basename(str(filename)).split('.')
            fileExt = nameAndExt[-1]
            if fileExt == 'lif':
                imLif = Import_lif(filename,self.par_obj,self.win_obj)
            if fileExt == 'tif' or fileExt == 'tiff':
                imTif = Import_tiff(filename,self.par_obj,self.win_obj)
            if fileExt == 'lsm':
                imTif = Import_lsm(filename,self.par_obj,self.win_obj)

                
        
            
        try:
            self.loadpath = str(QtCore.QFileInfo(filename).absolutePath())
            f = open(os.path.expanduser('~')+'/FCS_Analysis/configLoad', 'w')

            f.write(self.loadpath)
            f.close()

        
            
        except:
            print 'nofile'
        #Sets the first one to be plotted which triggers plotQueueFn
        
        
            

            
        







    
class Window(QtGui.QWidget):
    def __init__(self, par_obj, fit_obj):
        super(Window, self).__init__()
        self.fit_obj = fit_obj
        self.par_obj = par_obj
        self.generateWindow()
    def generateWindow(self):
        # a figure instance to plot on
        self.figure1 = plt.figure(figsize=(10,8))
        self.clickedS1 = None
        self.clickedS2 = None
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1 = FigureCanvas(self.figure1)
        self.figure1.patch.set_facecolor('white')
        self.toolbar1 = NavigationToolbar(self.canvas1, self)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        

        self.figure2 = plt.figure()
        self.canvas2 = FigureCanvas(self.figure2)
        
        #self.toolbar2 = NavigationToolbar(self.canvas2, self)

        self.figure3 = plt.figure()
        self.canvas3 = FigureCanvas(self.figure3)
        #self.toolbar3 = NavigationToolbar(self.canvas3, self)

        self.figure4 = plt.figure(figsize=(2,7))
        self.canvas4 = FigureCanvas(self.figure4)
        self.figure4.patch.set_facecolor('white')
        #self.toolbar4 = NavigationToolbar(self.canvas4, self)

        self.figure5 = plt.figure(figsize=(2,7))
        self.canvas5 = FigureCanvas(self.figure5)
        self.figure5.patch.set_facecolor('white')
        #Tself.toolbar5 = NavigationToolbar(self.canvas5, self)
        
        
        

        self.ex = FileDialog(self, par_obj, fit_obj)
        self.folderOutput = folderOutput(self)
        # Just some button connected to `plot` method
        self.openFile = QtGui.QPushButton('Open File')
        self.openFile.clicked.connect(self.ex.showDialog)
        self.replot_btn = QtGui.QPushButton('Replot Data')
        self.replot_btn.clicked.connect(self.plotDataQueueFn)
        self.replot_btn3 = QtGui.QPushButton('Replot Data')
        self.replot_btn3.clicked.connect(self.plotDataQueueFn)
        self.saveAll_btn = QtGui.QPushButton('Save Carpet')
        self.saveAll_btn.clicked.connect(self.save_carpets)

        
        #self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        #self.figure.canvas.mpl_connect('button_release_event', self.on_release)
        # set the layout
        self.spacer = QtGui.QLabel()
        main_layout = QtGui.QHBoxLayout()
        self.import_adv_btn = QtGui.QPushButton('Crop image')
        self.import_adv_btn.clicked.connect(self.import_adv_fn)
        self.reprocess_btn = QtGui.QPushButton('reprocess data')
        self.reprocess_btn.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn2 = QtGui.QPushButton('reprocess data')
        self.reprocess_btn2.clicked.connect(self.reprocessDataFn)
        self.reprocess_btn3 = QtGui.QPushButton('reprocess data')
        self.reprocess_btn3.clicked.connect(self.reprocessDataFn)
        
        self.mText = QtGui.QLabel('m (quality):')
        self.mText.resize(50,40)
        self.mEdit =lineEditSp('30',self, self.par_obj)
        self.mEdit.type ='m'
        self.DeltatText = QtGui.QLabel('Deltat (ms):')
        self.DeltatEdit = QtGui.QLabel()
        self.DeltatEdit.parObj = self
        self.DeltatEdit.type = 'deltat'
        
        
        self.folderSelect_btn = QtGui.QPushButton('Output Folder')
        self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)

        self.label =scanFileList(self,self.par_obj)
        self.GateScanFileListObj =GateScanFileList(self, self.par_obj)

        #The table which shows the details of the time-gating.
        self.modelTab = QtGui.QTableWidget(self)
        self.modelTab.setRowCount(0)
        self.modelTab.setColumnCount(6)
        
        
        self.modelTab.setColumnWidth(0,20);
        self.modelTab.setColumnWidth(1,40);
        self.modelTab.setColumnWidth(2,20);
        self.modelTab.setColumnWidth(3,40);
        self.modelTab.setColumnWidth(4,95);
        self.modelTab.setColumnWidth(5,60);
        self.modelTab.horizontalHeader().setStretchLastSection(True)
        self.modelTab.setMinimumSize(300,50)
        self.modelTab.setHorizontalHeaderLabels(QtCore.QString(",From: , ,To: ,, , , , ").split(","))

        #The table which shows the details of each correlated file. 
        self.modelTab2 = QtGui.QTableWidget(self)
        self.modelTab2.setRowCount(0)
        self.modelTab2.setColumnCount(6)
        self.modelTab2.setColumnWidth(0,80);
        self.modelTab2.setColumnWidth(1,140);
        self.modelTab2.setColumnWidth(2,30);
        self.modelTab2.setColumnWidth(3,100);
        self.modelTab2.setColumnWidth(4,100);
        self.modelTab2.setColumnWidth(5,100);
        self.modelTab2.horizontalHeader().setStretchLastSection(True)
        self.modelTab2.resize(800,400)
        self.modelTab2.setHorizontalHeaderLabels(QtCore.QString(",data name,plot, file name,,file name").split(","))

        tableAndBtns =  QtGui.QVBoxLayout()
        correlationBtns =  QtGui.QVBoxLayout()
        corrTopRow = QtGui.QHBoxLayout()
        corrBotRow = QtGui.QHBoxLayout()
        #self.label.setText('<HTML><H3>DATA file: </H3><P>'+str(6)+' Click here to load in this sample and what happens if I make it too long.</P></HTML>')
        #self.label.listId = 6
        self.fileDialog = QtGui.QFileDialog()
        self.centre_panel = QtGui.QVBoxLayout()
        self.right_panel = QtGui.QVBoxLayout()
        #Adds the main graph components to the top panel

        #LEFT PANEL
        self.left_panel = QtGui.QVBoxLayout()
        self.left_panel_top = QtGui.QHBoxLayout()
        self.left_panel.addLayout(self.left_panel_top)
        self.left_panel_top.addWidget(self.canvas4)
        self.left_panel_top.addWidget(self.canvas5)
        
        #LEFT PANEL TOP
        self.left_panel_top_btns= QtGui.QHBoxLayout()
        self.plotText =QtGui.QLabel()
        #self.plotText.setText('Plot: ')
        prevPane = QtGui.QPushButton('Prev pane')
        nextPane = QtGui.QPushButton('Next pane')


        #self.left_panel_top_btns.addWidget(self.plotText)
        self.spatialBinText = QtGui.QLabel()
        self.spatialBinText.setText('Integrated Bin Size: ')
        self.spatialBinEdit = QtGui.QSpinBox()
        self.spatialBinEdit.setRange(1,51);
        self.spatialBinEdit.setSingleStep(2)
        self.spatialBinEdit.parObj = self
        self.spatialBinEdit.resize(40,50)
        
        self.left_panel_top_btns.addWidget(prevPane)
        self.left_panel_top_btns.addWidget(nextPane)
        self.left_panel_top_btns.addWidget(self.spatialBinText)
        self.left_panel_top_btns.addWidget(self.spatialBinEdit)
        prevPane.clicked.connect(self.prevPaneFn)
        nextPane.clicked.connect(self.nextPaneFn)
        
        
        self.left_panel_top_btns.addStretch()
        self.left_panel.addLayout(self.left_panel_top_btns)


        #LEFT PANEL centre
        self.left_panel_centre = QtGui.QHBoxLayout()

        #LEFT PANEL centre right
        self.left_panel_centre_right = QtGui.QVBoxLayout()
        self.left_panel.addLayout(self.left_panel_centre)
        self.left_panel_centre.addWidget(self.modelTab)
        self.left_panel_centre.addLayout(self.left_panel_centre_right)

        self.left_panel_centre_right.setSpacing(2)
        self.left_panel_centre_right.addWidget(self.openFile)
        self.left_panel_centre_right.addWidget(self.import_adv_btn)
        self.left_panel_centre_right.addWidget(self.mText)
        self.left_panel_centre_right.addWidget(self.mEdit)
        self.left_panel_centre_right.addWidget(self.DeltatText)
        self.left_panel_centre_right.addWidget(self.DeltatEdit)
        self.left_panel_centre_right.addWidget(self.reprocess_btn)
        self.left_panel_centre_right.setAlignment(QtCore.Qt.AlignTop)
        
        self.right_panel.addWidget(self.canvas1)
        self.right_panel.addLayout(correlationBtns)
        self.right_panel.addWidget(self.modelTab2)

        self.bleachCorr_btn = QtGui.QPushButton('Photo Corr')
        self.bleachCorr_check_box=checkBoxSp2(self, par_obj)
        self.bleachCorr_check_box.obj = self
        self.displayCarpetText = QtGui.QLabel('Display: ')
        self.CH0Auto_btn = QtGui.QPushButton('CH0 Auto')
        self.CH1Auto_btn = QtGui.QPushButton('CH1 Auto')
        self.CH01Cross_btn = QtGui.QPushButton('CH01 Cross')
        self.addRegion_btn = QtGui.QPushButton('Save Region');
        self.export_region_btn = QtGui.QPushButton('Export to Fit');
        self.CH0Auto_btn.clicked.connect(self.CH0AutoFn)
        self.CH1Auto_btn.clicked.connect(self.CH1AutoFn)
        self.CH01Cross_btn.clicked.connect(self.CH01CrossFn)
        self.export_region_btn.clicked.connect(self.export_track_to_fit)
        self.TGScrollBoxObj = GateScanFileList(self,self.par_obj)
        self.bleachInt = bleachCorr(self.par_obj,self)
        self.bleachCorr_btn.clicked.connect(self.bleachInt.create_main_frame)
        
        
        corrBotRow.addWidget(self.replot_btn)
        corrBotRow.addWidget(self.folderSelect_btn)
        corrBotRow.addWidget(self.saveAll_btn)
        corrBotRow.addWidget(self.toolbar1)
        corrBotRow.setAlignment(QtCore.Qt.AlignLeft)
        
        corrTopRow.addWidget(self.bleachCorr_btn)
        corrTopRow.addWidget(self.bleachCorr_check_box)
        
        corrTopRow.addSpacing(10)
        corrTopRow.addWidget(self.displayCarpetText)
        corrTopRow.addWidget(self.CH0Auto_btn)
        corrTopRow.addWidget(self.CH1Auto_btn)
        corrTopRow.addWidget(self.CH01Cross_btn)
        corrTopRow.addWidget(self.addRegion_btn)
        corrTopRow.addWidget(self.export_region_btn)
        corrTopRow.setAlignment(QtCore.Qt.AlignLeft)

        tableAndBtns.addWidget(self.modelTab2)
        
        self.setLayout(main_layout)
        main_layout.addLayout(self.left_panel)
        correlationBtns.setSpacing(1.0)
        correlationBtns.addLayout(corrTopRow)
        correlationBtns.addLayout(corrBotRow)
        main_layout.addLayout(self.right_panel)
        
        #Where the image files are stored.
        



        gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1],width_ratios=[0.02, 0.98]) 
        self.plt1 = self.figure1.add_subplot(gs[0,:])
        self.plt2 = self.figure1.add_subplot(gs[1,1:])
        self.plt3 = self.figure1.add_subplot(gs[1,0:1])
        self.plt4= self.figure4.add_subplot(111)
        self.plt5= self.figure5.add_subplot(111)
        
        #self.colors = ['blue','green','red','cyan','magenta','yellow','black','white','blue','green','red','cyan','magenta','yellow','black','white','blue','green','red','cyan','magenta','yellow','black','white']
   
        self.figure1.suptitle('Correlation', fontsize=20)
        self.figure4.suptitle('Photon Count', fontsize=12)
        self.figure5.suptitle('Correlation Carpet', fontsize=12)
        self.figure5.suptitle('XT carpet', fontsize=12)
        self.carpetDisplay = 0
        self.multiSelect = GateScanFileList(self,self.par_obj)

        self.update_correlation_parameters()
    def import_adv_fn(self):
        print 'import'
        
        for b in range(0,self.par_obj.objectRef.__len__()):
            if self.par_obj.objectRef[b].plotOn == True:
                self.imp_adv_win = ImpAdvWin(self.par_obj,self,b)
                self.imp_adv_win.create_main_frame()


    def update_correlation_parameters(self):
        self.par_obj.spatialBin = int(self.spatialBinEdit.value())
        self.par_obj.m = float(self.mEdit.text())
        
    def CH0AutoFn(self):
            if self.bleachCorr_check_box.isChecked() == True:
                self.carpetDisplay = 3
            else:
                self.carpetDisplay = 0
            self.plotDataQueueFn()

    def CH1AutoFn(self):
            if self.bleachCorr_check_box.isChecked() == True:
                self.carpetDisplay = 4
            else:
                self.carpetDisplay = 1
            self.plotDataQueueFn()
    def CH01CrossFn(self):
            if self.bleachCorr_check_box.isChecked() == True:
                self.carpetDisplay = 5
            else:
                self.carpetDisplay = 2
            self.plotDataQueueFn()
    def save_carpets(self):
        """Saves the carpet raw data to an image file"""
        
        
        
        
        for objId in self.objectRef:
            if(objId.cb.isChecked() == True):
                height = objId.AutoCorr_carpetCH0.shape[1]
                width = objId.AutoCorr_carpetCH0.shape[0]
                
                self.plot_PhotonCount(objId)
                if objId.numOfCH ==1:
                    if objId.bleachCorr == True:
                        export_im =np.zeros((2,height,width))
                        export_im[0,:,:] = objId.AutoCorr_carpetCH0[:,:].T;
                        export_im[1,:,:] = objId.AutoCorr_carpetCH0_pc[:,:].T;
                    else:
                        export_im =np.zeros((height,width))
                        export_im[:,:] = objId.AutoCorr_carpetCH0[:,:].T;

                if objId.numOfCH ==2:
                    if objId.bleachCorr == True:
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

        
        #self.plt5.a = FCSfn.Annotate(self,self.GateScanFileListObj)
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

        #if object.type == 'scanObject':
        yLimMn = int(((objId.pane)*(objId.CH0.shape[1]/64)*150))
        yLimMx = int(((objId.pane+1)*(objId.CH0.shape[1]/64)*150))
        
        #barX = object.timeSeriesScale1[::-1]#*object.deltat
        #barX = np.array(object.timeSeries1).astype(np.float32)[::-1]
        #barXC = barX[yLimMn:yLimMx]
        self.plt4.barh(np.arange(yLimMx,yLimMn,-1)-0.5,objId.CH0_arraySum[yLimMn:yLimMx][::-1], height=1, color=objId.color,linewidth=0)
        
        #if object.numOfCH == 2:
        #    barX = object.timeSeriesScale2[::-1]*object.deltat
        #    barY = np.array(object.timeSeries2).astype(np.float32)[::-1]
        #    self.plt4.barh(barX[yLimMn:yLimMx],np.arange(yLimMn,yLimMx), height=object.photonCountBin,color="grey",linewidth=0,edgecolor = None)
        
        self.plt4.set_xlim(0,objId.maxCountCH0)
        self.plt4.set_ylim(yLimMx,yLimMn)

        self.figure4.subplots_adjust(left=0.30,)
        self.plt4.tick_params(axis='both', which='major', labelsize=8)
        
        self.plt4.set_xlabel('Photon Counts (-ve CH0, +ve CH1)', fontsize=8)
        self.plt4.set_ylabel('Line (pixels)', fontsize=14)
        self.plt4.xaxis.grid(True,'minor')
        self.plt4.xaxis.grid(True,'major')
        self.plt4.yaxis.grid(True,'minor')
        self.plt4.yaxis.grid(True,'major')
        self.plt4.set_autoscale_on(False)
        self.canvas4.draw()

            
    def plot(self,object):
        ''' plots correlation functions '''

        autotime = object.autotime
        
        auto = object.autoNorm
        corrText = 'Auto-correlation'
        
        
        
        
        
        self.plt1.plot(autotime,auto[:,0,0],object.color)
        self.plt1.set_xscale('log')
        
        
        self.plt1.set_xlabel('Pixels', fontsize=12)
        self.plt1.set_ylabel(corrText+' CH0', fontsize=12)
        self.plt1.xaxis.grid(True,'minor')
        self.plt1.xaxis.grid(True,'major')
        self.plt1.yaxis.grid(True,'minor')
        self.plt1.yaxis.grid(True,'major')
        
        
        
        

        #if object.type == 'scanObject':
        yLimMn = (object.pane)*(object.CH0.shape[1]/64)*150
        yLimMx = (object.pane+1)*(object.CH0.shape[1]/64)*150
        if object.numOfCH ==1:
            image=object.CH0[yLimMn:yLimMx,:]
        elif object.numOfCH ==2:
            image = np.zeros((int(yLimMx-yLimMn),object.CH0.shape[1],3))
            image[:,:,0]=object.CH0[yLimMn:yLimMx,:]
            image[:,:,1]=object.CH1[yLimMn:yLimMx,:]
        #if object.correlation_carpet == True:
        
        self.plt5.imshow(((image)/np.max(image)),interpolation = 'nearest',extent=[0,object.CH0.shape[1],yLimMx,yLimMn])#,extent=[0,object.CH0.shape[1],np.max(autotime),0],aspect='auto')
       
        self.figure5.subplots_adjust(left=0.1,right=0.95)
        self.plt5.set_xlabel('Column pixels', fontsize=12)

        self.plt5.set_ylabel('Tau (ms)', fontsize=14)
        self.plt5.tick_params(axis='both', which='major', labelsize=8)
        self.plt5.autoscale(False)
        
        self.canvas5.draw()

        #self.corrArrScale, self.AutoCorr_carpetCH0, self.AutoCorr_carpetCH1, self.CrossCorr_carpet01
        if self.carpetDisplay == 0:
            img = np.flipud(object.AutoCorr_carpetCH0[:,:].T);
            sum_img = np.flipud(object.CH0_arrayColSum)
        if self.carpetDisplay == 1:
            img = np.flipud(object.AutoCorr_carpetCH1[:,:].T);
            sum_img = np.flipud(object.CH1_arrayColSum)
        if self.carpetDisplay == 2:
            img = np.flipud(object.CrossCorr_carpet01[:,:].T);
            sum_img = np.flipud(object.CH0_arrayColSum)
        if self.carpetDisplay == 3:
            img = np.flipud(object.AutoCorr_carpetCH0_pc[:,:].T);
            sum_img = np.flipud(object.CH0_arrayColSum)
        if self.carpetDisplay == 4:
            img = np.flipud(object.AutoCorr_carpetCH1_pc[:,:].T);
            sum_img = np.flipud(object.CH1_arrayColSum)
        if self.carpetDisplay == 5:
            img = np.flipud(object.CrossCorr_carpet01_pc[:,:].T);
            sum_img = np.flipud(object.CH0_arrayColSum)


        
        #pickle.dump(autotime,open('autotime.pkl', 'wb'))
        #pickle.dump(image.T,open('data.pkl', 'wb'))

        c = np.logspace(np.log10(autotime[0]), np.log10(autotime[-1]), img.shape[1], endpoint=True)
        e =[]
        for i in range(0,img.shape[1]):
            e.append(min(enumerate(autotime), key=lambda x:abs(x[1]-c[i]))[0])
        imgN = np.zeros(img.shape)
        imgN = img[:,e]

        imgN[imgN < 0]=0;
        for i in range(0, img.shape[0]):
            
            imgN[i,:] = imgN[i,:]/np.max(imgN[i,:])


        self.plt2.set_xlabel('Time (ms)', fontsize=12)
        self.plt2.set_ylabel('Column pixels', fontsize=14)
        
        
        im = self.plt2.imshow(imgN, extent=[autotime[0],autotime[-1],0,img.shape[0]],interpolation ='nearest',aspect='auto')
        

        

        try:
            self.tfig.delaxes(self.tfig.axes[2]) 
           
        except:
            pass

        im1 = self.plt3.imshow(sum_img.reshape(object.CH0_arrayColSum.shape[0],1),extent=[0,5,0,img.shape[0]],interpolation = 'nearest',aspect='auto',cmap=cm.Reds_r);
        self.plt3.set_ylabel('Intensity maxima')
        self.plt3.set_xticklabels('')

        #divider = make_axes_locatable(self.plt2)
        #self.ax_cb = divider.new_horizontal(size="1%", pad=0.10)
        #self.tfig = self.plt2.get_figure()
        #self.tfig.add_axes(self.ax_cb)
        #cb = plt.colorbar(im, cax=self.ax_cb)
        self.plt2.set_xscale('log')

        

        

        self.canvas1.draw()
        self.plt1.cla()
        self.plt2.b = ClickMovie(self.par_obj,self,self.plt2,object,self.multiSelect)
        
        self.addRegion_btn.clicked.connect(self.plt2.b.saveRegion)
        #self.plt5.b = ClickMovie(self,self.plt5)
        
        self.figure1.subplots_adjust(left=0.1,right=0.90)
        self.plt2.autoscale(False)
        self.plt2.b.draw_line()
        self.plt2.b.draw_selection()
        
        #self.plt2.tick_params(axis='both', which='major', labelsize=8)
        #.canvas.mpl_connect('pick_event', onpick4)
        #self.figure1.canvas.mpl_connect('button_release_event', button_release_callback)
        # refresh canvas
        self.canvas1.draw()
    def export_track_to_fit(self):

        xmin = int(self.clickedS1)
        xmax = int(self.clickedS2)-1
        self.export_track_fn(xmin,xmax)
    def export_track_fn(self,xmin,xmax):

        #Checks if the plot is on or not.
        for objId in self.par_obj.objectRef:
            if(objId.cb.isChecked() == True):
                for i in range(xmin, xmax+1):
                    
                    corrObj1 = corrObject(objId.filepath,self.fit_obj);
                    corrObj1.siblings = None
                    self.fit_obj.objIdArr.append(corrObj1.objId)
                    corrObj1.param = copy.deepcopy(self.fit_obj.def_param)
                    corrObj1.ch_type = 0
                    corrObj1.prepare_for_fit()
                    corrObj1.autotime = objId.corrArrScale[:]
                    corrObj1.kcount = objId.kcountCH0[i]
                    corrObj1.numberNandB = objId.numberNandBCH0[i]
                    corrObj1.brightnessNandB = objId.brightnessNandBCH0[i]
                    corrObj1.type = "scan"
                    corrObj1.siblings = None

                    if self.bleachCorr_check_box.isChecked() == True:
                        corrObj1.name = objId.name+'row_'+str(i)+'_CH0_Auto_Corr_pc'
                        corrObj1.autoNorm = objId.AutoCorr_carpetCH0_pc[:,i]
                    else:
                        corrObj1.name = objId.name+'row_'+str(i)+'_CH0_Auto_Corr'
                        corrObj1.autoNorm = objId.AutoCorr_carpetCH0[:,i]
                    
                    
                    if objId.numOfCH == 2:
                        corrObj2 = corrObject(objId.filepath,self.fit_obj);
                        corrObj2.siblings = None
                        self.fit_obj.objIdArr.append(corrObj2.objId)
                        corrObj2.ch_type = 1
                        corrObj2.param = copy.deepcopy(self.fit_obj.def_param)
                        corrObj2.prepare_for_fit()
                        corrObj2.autotime = objId.corrArrScale[:]
                        corrObj2.kcount = objId.kcountCH1[i]
                        corrObj2.numberNandB = objId.numberNandBCH1[i]
                        corrObj2.brightnessNandB = objId.brightnessNandBCH1[i]
                        corrObj2.type = "scan"
                        if self.bleachCorr_check_box.isChecked() == True:
                            corrObj2.name = objId.name+'row_'+str(i)+'_CH1_Auto_Corr_pc'
                            corrObj2.autoNorm = objId.AutoCorr_carpetCH1_pc[:,i]
                        else:
                            corrObj2.name = objId.name+'row_'+str(i)+'_CH1_Auto_Corr'
                            corrObj2.autoNorm = objId.AutoCorr_carpetCH1[:,i]
                        
                        

                        corrObj3 = corrObject(objId.filepath,self.fit_obj);
                        corrObj3.siblings = None
                        self.fit_obj.objIdArr.append(corrObj3.objId)
                        
                        corrObj3.ch_type = 2
                        corrObj3.param = copy.deepcopy(self.fit_obj.def_param)
                        corrObj3.prepare_for_fit()
                        corrObj3.autotime = objId.corrArrScale[:]
                        if self.bleachCorr_check_box.isChecked() == True:
                            corrObj3.name = objId.name+'row_'+str(i)+'_CH01_Auto_Corr_pc'
                            corrObj3.autoNorm = objId.CrossCorr_carpet01_pc[:,i]

                        else:
                            corrObj3.name = objId.name+'row_'+str(i)+'_CH01_Auto_Corr'
                            corrObj3.autoNorm = objId.CrossCorr_carpet01[:,i]
                        corrObj3.param = copy.deepcopy(self.fit_obj.def_param)

                        corrObj1.siblings = [corrObj2,corrObj3]
                        corrObj2.siblings = [corrObj1,corrObj3]
                        corrObj3.siblings = [corrObj1,corrObj2]

                    self.fit_obj.fill_series_list()


        
        
class ClickMovie():
        def __init__(self,par_obj, win_obj, axis,objectId,multiSelect):
            self.axis=axis
            plt.sca(self.axis)
            self.objectId = objectId
            self.x0 = []
            self.par_obj = par_obj
            self.win_obj = win_obj
            self.rect =[]
            self.multiSelect = multiSelect
            self.pickerSelect = False;
            win_obj.figure1.canvas.mpl_connect('button_press_event', self.on_press)
            win_obj.figure1.canvas.mpl_connect('button_release_event', self.on_release)
            

        def on_press(self, event):
            plt.sca(self.axis)
            #self.ax.figure.canvas.draw()
            self.y0 = event.ydata
            self.rect.append(plt.axhspan(self.y0 , self.y0, edgecolor='black', facecolor ='none',linewidth=1.5))
            self.win_obj.canvas1.draw()
            

        def on_release(self, event):
            #self.rect.remove()
            self.x1 = event.xdata
            
            if(self.x0 <0): self.x0 =0
            if(self.x1 <0): self.x1 =0
            if(self.x0 >self.x1): self.x1b =self.x0;self.x0=self.x1;self.x0=self.x1b
            for i in range(0,self.rect.__len__()):
                #    self.scrollBox.rect[i].remove()
                self.rect[i].remove()
            self.rect =[]
            if event.xdata != None:
                if self.y0>=event.ydata:
                    s2d = np.ceil(self.y0)
                    s1d = np.floor(event.ydata)
                    #s2d =(s1)-1
                    #s1d =(s2)+1
                else:
                    s2d = np.floor(event.ydata)
                    s1d = np.ceil(self.y0)
                    #s1d =(s1)+1
                    #s2d =(s2)-1
                #print 'event.ydata', event.ydata
                #print 'self.y0',self.y0
                #print 's1d',s1d
                #print 's2d',s2d

                self.rect.append(plt.axhspan( s1d,s2d, edgecolor='black', facecolor ='none',linewidth=1.5))
                
                
                
                self.win_obj.clickedS1 = int(s1d)
                self.win_obj.clickedS2 = int(s2d)
                self.draw_line()


                
        def saveRegion(self):
                #Appends value to array
                self.multiSelect.x0.append( self.win_obj.clickedS1)
                self.multiSelect.x1.append( self.win_obj.clickedS2-1)
                self.multiSelect.color = self.par_obj.colors[self.multiSelect.rect.__len__()]
                self.multiSelect.TGid.append(self.multiSelect.TGnumOfRgn)
                self.multiSelect.facecolor.append(self.par_obj.colors[self.multiSelect.TGnumOfRgn])
                self.par_obj.TGnumOfRgn = self.par_obj.TGnumOfRgn + 1
                #Regenerates list.
                self.multiSelect.generateList()
        def draw_selection(self):
                if self.win_obj.clickedS1 != None  and self.win_obj.clickedS2 != None:
                    plt.sca(self.axis)
                    #self.ax.figure.canvas.draw()
                    
                    self.rect.append(plt.axhspan(self.win_obj.clickedS1 , self.win_obj.clickedS2 , edgecolor='black', facecolor ='none',linewidth=1))
                    self.win_obj.canvas1.draw()

        def draw_line(self):
                self.win_obj.plt1.cla()
                #self.parObj.plt1.set_autoscale_on(True)
                
                
                self.win_obj.plt1.set_xscale('log');
                self.win_obj.plt1.set_ylabel('Column pixels', fontsize=14)
                if self.win_obj.clickedS1 != None  and self.win_obj.clickedS2 != None:
                    for b in range(self.win_obj.clickedS1,self.win_obj.clickedS2):
                        self.win_obj.plt1.set_autoscale_on(True)
                        if self.win_obj.bleachCorr_check_box.isChecked() == True:
                            if self.win_obj.carpetDisplay == 3:
                                self.win_obj.plt1.plot(self.objectId.corrArrScale ,self.objectId.AutoCorr_carpetCH0_pc[:,int(b)],self.objectId.color)
                            if self.win_obj.carpetDisplay == 4:
                                self.win_obj.plt1.plot(self.objectId.corrArrScale ,self.objectId.AutoCorr_carpetCH1_pc[:,int(b)],self.objectId.color)
                            if self.win_obj.carpetDisplay == 5:
                                self.win_obj.plt1.plot(self.objectId.corrArrScale ,self.objectId.CrossCorr_carpet01_pc[:,int(b)],self.objectId.color)
                        else:
                            if self.win_obj.carpetDisplay == 0:
                                self.win_obj.plt1.plot(self.objectId.corrArrScale ,self.objectId.AutoCorr_carpetCH0[:,int(b)],self.objectId.color)
                            if self.win_obj.carpetDisplay == 1:
                                self.win_obj.plt1.plot(self.objectId.corrArrScale ,self.objectId.AutoCorr_carpetCH1[:,int(b)],self.objectId.color)
                            if self.win_obj.carpetDisplay == 2:
                                self.win_obj.plt1.plot(self.objectId.corrArrScale ,self.objectId.CrossCorr_carpet01[:,int(b)],self.objectId.color)
                        
                        a,b = self.win_obj.plt1.get_ylim()
                        self.win_obj.plt1.set_ylim(bottom=0,top=b)
                    self.win_obj.canvas1.draw()


class lineEditSp(QtGui.QLineEdit):
    def __init__(self,text,win_obj,par_obj):
        QtGui.QLineEdit.__init__(self,text)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.parObj = par_obj
        self.win_obj = win_obj
        self.obj = []
        self.type = []
        self.TGid =[]
    def __handleEditingFinished(self):
        self.parObj.m = float(self.text())
        print 'activated go go.'
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
        self.parObj = []
        self.win_obj = win_obj
        self.par_obj = par_obj
    def __activated(self):
        self.xmin = int(self.win_obj.multiSelect.x0[self.TGid])
        self.xmax = int(self.win_obj.multiSelect.x1[self.TGid])
        self.win_obj.export_track_fn(self.xmin,self.xmax)
        

                        
class checkBoxSp3(QtGui.QCheckBox):
    def __init__(self, par_obj, win_obj):
        QtGui.QCheckBox.__init__(self)
        self.obj = []
        self.type = []
        self.name =[]
        self.par_obj = par_obj
        self.win_obj = win_obj
    def updateChecked(self):
        print self.isChecked()
        print self.obj
        if self.isChecked() == True:  

            for objId in self.par_obj.objectRef:
                if objId != self.obj:
                    objId.plotOn = False
                    objId.cb.setChecked(False)
                    self.win_obj.DeltatEdit.setText(str(objId.deltat));

        
        
            self.obj.plotOn = self.isChecked()
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
            a.setText('<HTML><p style="color:'+str(self.par_obj.colors[i% len(self.par_obj.colors)])+';margin-top:0">'+type_obj+' : </p></HTML>')
            

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
            sb = pushButtonSp2('save file')
            sb.parObj = self.par_obj
            sb.obj = self.par_obj.objectRef[i]
            self.win_obj.modelTab2.setCellWidget(i, 4, sb)

            b = baseList()
            b.setText('<HTML><p style="margin-top:0">'+self.par_obj.objectRef[i].ext+' file :'+str(self.par_obj.data[i])+' </p></HTML>')
            self.win_obj.modelTab2.setCellWidget(i, 5, b)
            
            
            #self.parObj.label.objCheck.append(cb)
            j = i+1
        
        

class GateScanFileList():
    #Generates scroll box for time-gating data.
    def __init__(self, win_obj, parObj):
        self.TGnumOfRgn = 0
        self.x0 =[]
        self.x1 =[]
        self.facecolor =[]
        self.TGid = []
        self.rect =[]
        self.parObj = parObj
        self.win_obj = win_obj

    def generateList(self):
        for i in range(0, self.parObj.TGnumOfRgn):
                self.win_obj.modelTab.setRowCount(i+1)
                
                txt2 = QtGui.QLabel()
                txt2.setText('<HTML><p style="color:'+str(self.parObj.colors[i])+';margin-top:0">t0:</p></HTML>')
                self.win_obj.modelTab.setCellWidget(i, 0, txt2)


                lb1 = lineEditSp(str(self.x0[i]),self,self.parObj)
                lb1.setMaxLength(5)
                lb1.setFixedWidth(40)
                lb1.setText(str(self.x0[i]))
                lb1.type = 'tgt0'
                lb1.TGid = i
                self.win_obj.modelTab.setCellWidget(i, 1, lb1)

                txt3 = QtGui.QLabel()
                txt3.setText('<HTML><p style="color:'+str(self.parObj.colors[i])+';margin-top:0">t1:</p></HTML>')
                self.win_obj.modelTab.setCellWidget(i, 2, txt3)
                
                

                lb2 = lineEditSp(str(self.x1[i]),self,self.parObj)
                
                lb2.setMaxLength(5)
                lb2.setFixedWidth(40)
               
                lb2.type = 'tgt1'
                lb2.TGid = i
                self.win_obj.modelTab.setCellWidget(i, 3, lb2)
                #txt4 = QtGui.QLabel()
               

                #photoCrr_btn = FCSfn.pushButtonSp(self)
                #Populates comboBox with datafiles to which to apply the time-gating.
                #photoCrr_btn.TGid = i
                #photoCrr_btn.parObj =self.parObj
                #photoCrr_btn.xmin =self.x0[i]
                #photoCrr_btn.xmax = self.x1[i]
                #photoCrr_btn.type = 'photoCrr'


                #self.parObj.modelTab.setCellWidget(i, 4, photoCrr_btn)
                cbtn = pushButtonSp('Export to fit',self.win_obj,self.parObj)
            
                cbtn.TGid = i
                cbtn.xmin = int(self.x0[i])
                cbtn.xmax = int(self.x1[i])
                self.win_obj.modelTab.setCellWidget(i, 4, cbtn)
                #Make sure the btn knows which list it is connected to.
                #cbtn.objList = cbx
class pushButtonSp2(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self,parent)
        self.clicked.connect(self.__clicked)
        self.obj =[];
    def __clicked(self):
        print self.obj.autotime
        f = open(main.folderOutput.filepath+'/'+self.obj.name+'_CH1_Auto_Corr.csv', 'w')
        f.write('# Time (ns)\tCH1 Auto-Correlation\n')
        for x in range(0,self.obj.autotime.shape[0]):
            f.write(str(int(self.obj.autotime[x][0]))+','+str(self.obj.autoNorm[x,0,0])+ '\n')

        f = open(main.folderOutput.filepath+'/'+self.obj.name+'_CH2_Auto_Corr.csv', 'w')
        f.write('# Time (ns)\tCH2 Auto-Correlation\n')
        for x in range(0,self.obj.autotime.shape[0]):
            f.write(str(int(self.obj.autotime[x][0]))+','+str(self.obj.autoNorm[x,1,1])+ '\n')
        
        f = open(main.folderOutput.filepath+'/'+self.obj.name+'_CH1_Cross_Corr.csv', 'w')
        f.write('# Time (ns)\tCH1 Cross-Correlation\n')
        for x in range(0,self.obj.autotime.shape[0]):
            f.write(str(int(self.obj.autotime[x][0]))+','+str(self.obj.autoNorm[x,0,1])+ '\n')
        
        f = open(main.folderOutput.filepath+'/'+self.obj.name+'_CH2_Cross_Corr.csv', 'w')
        f.write('# Time (ns)\tCH2 Cross-Correlation\n')
        for x in range(0,self.obj.autotime.shape[0]):
            f.write(str(int(self.obj.autotime[x][0]))+','+str(self.obj.autoNorm[x,1,0])+ '\n')
        print 'file Saved'
class folderOutput(QtGui.QMainWindow):
    
    def __init__(self,parent):
        super(folderOutput, self).__init__()
       
        self.initUI()
        self.parent = parent
        self.parent.config ={}
        
        try:
            self.parent.config = pickle.load(open(os.path.expanduser('~')+'/FCS_Analysis/config.p', "rb" ));
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
                pickle.dump(self.parent.config, open(str(os.path.expanduser('~')+'/FCS_Analysis/config.p'), "w" ))              
def functionTest():
    print 'working test:'
class checkBoxSp2(QtGui.QCheckBox):
    def __init__(self, win_obj, par_obj):
        QtGui.QCheckBox.__init__(self)
        self.obj = []
        self.type = []
        self.name =[]
        self.stateChanged.connect(self.__changed)
    def __changed(self,state):
        
        if state == 2:
            if self.obj.carpetDisplay == 0:
                self.obj.CH0AutoFn()
            if self.obj.carpetDisplay == 1:
                self.obj.CH1AutoFn()
            if self.obj.carpetDisplay == 2:
                self.obj.CH01CrossFn()
        if state == 0:
            if self.obj.carpetDisplay == 3:
                self.obj.CH0AutoFn()
            if self.obj.carpetDisplay == 4:
                self.obj.CH1AutoFn()
            if self.obj.carpetDisplay == 5:
                self.obj.CH01CrossFn()
class baseList(QtGui.QLabel):
    def __init__(self):
        super(baseList, self).__init__()
        self.listId=0
    def mousePressEvent(self,ev):
        print self.listId
class ParameterClass():
    def __init__(self):
        
        #Where the data is stored.
        self.data = []
        self.objectRef =[]
        self.data = []
        self.ax_cb = [];
        self.numOfLoaded = 0
        self.TGnumOfRgn =0
        self.start_pt = 0
        self.end_pt = 0
        self.interval_pt = 1
        self.colors = ['blue','green','red','cyan','magenta','yellow','black']  
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    win_tab = QtGui.QTabWidget()
    par_obj = ParameterClass()
    fit_obj = Form()
    fit_obj.app = app
    
    mainWin = Window(par_obj,fit_obj)
    
    win_tab.addTab(mainWin, "Load scanning data")
    win_tab.addTab(fit_obj, "Fit Function")
    win_tab.resize(1200,800)
    
    #path = '../../'
    #filename = 'Scanning_FCS_TopfluorPE_Atto647N.tif'
    #filepath = path+filename
    #picoObj  = scanObject(filepath);
    #plotDataQueueFn()
    
    
    
    
    
    

    
    
    win_tab.show()



    sys.exit(app.exec_())

    
