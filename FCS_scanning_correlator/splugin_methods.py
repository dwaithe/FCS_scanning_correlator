from PyQt4 import QtGui, QtCore
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.lines as lines
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
from matplotlib.patches import Rectangle
from correlation_objects import scanObject
class ImpAdvWin(QtGui.QMainWindow):
    def __init__(self,par_obj,win_obj,obj_id_num):
        QtGui.QMainWindow.__init__(self)
        self.par_obj = par_obj;
        self.win_obj = win_obj;
        self.objId = self.par_obj.objectRef[obj_id_num]
        
        self.num_of_lines = self.objId.num_of_lines;
        self.start_pt = 0;
        self.end_pt = self.objId.num_of_lines;
        self.interval_pt = 1;

    def create_main_frame(self):
        page = QtGui.QWidget() 

        



        hbox_main = QtGui.QHBoxLayout()
        vbox1 = QtGui.QVBoxLayout()
        vbox2 = QtGui.QVBoxLayout()

        hbox_main.addLayout(vbox1)
        hbox_main.addLayout(vbox2)

        #Crop settings.
        crop_panel = QtGui.QGroupBox('Import Crop Settings')

        self.start_pt_txt = QtGui.QLabel('Start point: ');
        self.end_pt_txt = QtGui.QLabel('End point: ');
        self.interval_pt_txt = QtGui.QLabel('Num of Intervals ');
        self.start_pt_sp = QtGui.QSpinBox()
        self.end_pt_sp = QtGui.QSpinBox()
        self.interval_pt_sp = QtGui.QSpinBox()

        

        #Set limits on the spinboxes
        self.start_pt_sp.setMinimum(0)
        self.start_pt_sp.setMaximum(self.num_of_lines)
        self.end_pt_sp.setMinimum(0)
        self.end_pt_sp.setMaximum(self.num_of_lines)
        self.interval_pt_sp.setMinimum(1)
        self.interval_pt_sp.setMaximum(20)
        
        self.start_pt_sp.setValue(self.start_pt)
        self.end_pt_sp.setValue(self.end_pt)
        self.interval_pt_sp.setValue(1)
        self.start_pt_sp.valueChanged[int].connect(self.plotData)
        self.end_pt_sp.valueChanged[int].connect(self.plotData)
        self.interval_pt_sp.valueChanged[int].connect(self.plotData)


        reprocess_btn = QtGui.QPushButton('Reprocess Data')
        apply_to_imports =  QtGui.QCheckBox('Apply to Subsequent Imports')
        store_profile = QtGui.QPushButton('Store profile')
        import_profile =QtGui.QPushButton('Import profile')

        left_grid = QtGui.QGridLayout()
        crop_panel.setLayout(left_grid)
        left_grid.addWidget(self.start_pt_txt,1,0)
        left_grid.addWidget(self.end_pt_txt,2,0)
        left_grid.addWidget(self.interval_pt_txt,3,0)
        left_grid.addWidget(self.start_pt_sp,1,1)
        left_grid.addWidget(self.end_pt_sp,2,1)
        left_grid.addWidget(self.interval_pt_sp,3,1)

        reprocess_btn.clicked.connect(self.reprocess_and_create)
        
        vbox1.addWidget(crop_panel)
        vbox1.addWidget(reprocess_btn)
        #vbox1.addWidget(apply_to_imports)
        #vbox1.addWidget(store_profile)
        #vbox1.addWidget(import_profile)


        

        self.figure1 = Figure(figsize=(32,2), dpi=100)

        self.canvas1 = FigureCanvas(self.figure1)
        self.figure1.patch.set_facecolor('white')
        self.plt1 = self.figure1.add_subplot(1, 1, 1)
        

        #Makes sure it spans the whole figure.
        #self.figure1.subplots_adjust(left=0.001, right=0.999, top=0.999, bottom=0.001)
        vbox2.addWidget(self.canvas1)
        page.setLayout(hbox_main)
        self.setCentralWidget(page)
        
        self.plotData()
        self.show()
    def plotData(self):
        self.start_pt = self.start_pt_sp.value()
        self.end_pt = self.end_pt_sp.value()
        self.interval_pt = self.interval_pt_sp.value()
        self.par_obj.start_pt = self.start_pt
        self.par_obj.end_pt = self.end_pt
        self.par_obj.interval_pt = self.interval_pt
        
        self.plt1.cla()
        #Calculate the total integral
        totalFn = np.sum(self.objId.CH0, 1).astype(np.float64)
        #Plot 1 in 10 pixels from the Gasussian.
        self.plt1.plot(range(0,totalFn.shape[0],10) ,totalFn[0::10],'blue')
        #If plotting with correction:
        self.plt1.set_xlim(0,self.num_of_lines)
        
        if self.objId.numOfCH == 2:
            totalFn = np.sum(self.objId.CH1, 1).astype(np.float64)
            self.plt1.plot(range(0,totalFn.shape[0],10) ,totalFn[0::10],'red')
            
        
        for i in range(0,self.interval_pt):
            interval = (self.end_pt-self.start_pt)/self.interval_pt
            st = np.round(self.start_pt + (interval*i),0)
            en = np.round(self.start_pt + ((interval)*(i+1)), 0)
            self.plt1.axvspan(st, en,  edgecolor=None, facecolor =self.par_obj.colors[i % len(self.par_obj.colors)],alpha=0.4,linewidth=0,picker =True)
        #self.plt1.axvspan(1,2 ,  edgecolor='black', facecolor ='red',linewidth=1.5,picker =True)
        #ted = self.plt1.axvspan(2,3 ,  edgecolor='black', facecolor ='green',linewidth=1.5,picker =True)
        #self.canvas1.draw()
        self.plt1.figure.canvas.draw()
        #ted.remove()
        #self.draw_region()
        
    def draw_region(self):
        self.rect = []
        
        
        
        self.canvas1.draw()
        plt.show()
    def reprocess_and_create(self):
        
        
        s =[]
        for i in range(0,self.par_obj.interval_pt):
            interval = (self.par_obj.end_pt-self.par_obj.start_pt)/self.par_obj.interval_pt
            st = np.round(self.par_obj.start_pt + (interval*i),0)
            en = np.round(self.par_obj.start_pt + ((interval)*(i+1)), 0)
            s.append(scanObject(self.objId.filepath,self.par_obj,self.objId.imDataDesc,self.objId.imDataStore,st,en));
            s[-1].type = self.objId.type+' sub '+str(s[-1].unqID)
            s[-1].name = s[-1].name+ '_sub_'+str(s[-1].unqID)+'_'
        #self.win_obj.canvas1.draw()
        self.win_obj.label.generateList()
        self.win_obj.GateScanFileListObj.generateList()
        


class bleachCorr(QtGui.QMainWindow):
    def __init__(self,parObj,win_obj):
        QtGui.QMainWindow.__init__(self)
        #self.fileArray = fileArray
        #self.create_main_frame()
        self.parObj = parObj
        self.win_obj = win_obj
        self.corrFn = False
        

    def create_main_frame(self):
        for objId in self.parObj.objectRef:
            if(objId.cb.isChecked() == True):
                self.objId=objId
                break;
        self.corrFn = False      
        #self.trace_idx = self.parObj.clickedS1

        page = QtGui.QWidget()        
        hbox_main = QtGui.QHBoxLayout()
        vbox1 = QtGui.QVBoxLayout()
        vbox0 = QtGui.QVBoxLayout()
        self.setWindowTitle("Bleach correction")
        self.figure1 = plt.figure(figsize=(10,4))
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas1 = FigureCanvas(self.figure1)
        
        self.figure1.patch.set_facecolor('white')
        self.canvas1 = FigureCanvas(self.figure1)

        if objId.numOfCH ==1:
            self.plt1 = self.figure1.add_subplot(1,1,1)

        elif objId.numOfCH == 2:
            self.plt1 = self.figure1.add_subplot(1,2,1)
            self.plt2 = self.figure1.add_subplot(1,2,2)
        
        
        
        self.export_trace_btn = QtGui.QPushButton('Apply to Data')
        self.vbox2 = QtGui.QHBoxLayout()
        self.apply_corr_btn = QtGui.QPushButton('Generate Correction')
        #hbox1.addLayout(vbox1)
        self.export_trace_btn.clicked.connect(self.outputData)
        self.apply_corr_btn.clicked.connect(self.plot_corrFn)
        #vbox0.addLayout(hbox1)
        hbox_main.addLayout(vbox0)
        hbox_main.addLayout(vbox1)
        
        
        
        vbox0.addLayout(self.vbox2)
        vbox0.addWidget(self.apply_corr_btn)
        vbox0.addWidget(self.export_trace_btn)
        vbox0.addStretch();
        vbox1.addWidget(self.canvas1)
        
        page.setLayout(hbox_main)
        self.setCentralWidget(page)
        self.show()
        self.plotData()
        #self.
        #self.connect(self.button, QtCore.SIGNAL("clicked()"), self.clicked)
    def export_traceFn(self):
        corrObj= corrObject(self.objId.filepath,form);
        form.objIdArr.append(corrObj.objId)
        corrObj.name = self.objId.name+'_CH0_Auto_Corr'
        corrObj.updateFitList()
        corrObj.autoNorm = np.array(self.corltd_corr[:,1]).reshape(-1)
        corrObj.autotime = np.array(self.corltd_corr[:,0]).reshape(-1)
        corrObj.param = form.def_param
        form.fill_series_list(form.objIdArr)
    
    def plot_corrFn(self):
        self.corrFn = True
        self.plotData()
    def learn_corr_fn(self,totalFn):
        """Calculates the correction and generates output."""
        def_param = Parameters()
        def_param.add('f0', value=totalFn[0], vary=True)
        def_param.add('tb', min =0, value=20000.0, vary=True)
        res = minimize(self.residual, def_param, args=(np.arange(0,totalFn.__len__()),np.array(totalFn).astype(np.float64)))
        
        x= np.arange(0,totalFn.__len__())
        #The useful parameters
        return self.equation_(def_param,x), def_param['f0'].value
    def apply_corr_fn(self,inFn,ratio):
        """Applys the correction to the file."""
        wei = self.weightings/ratio
        l_f0 = self.learn_f0/ratio
        outFn = (inFn[:]/np.sqrt(wei[:]/l_f0))+ (l_f0*(1-np.sqrt(wei[:]/l_f0)))
        return outFn
    def equation_(self,param, x):
        """The equation used for photobleach correction"""
        f0 = param['f0'].value; tb = param['tb'].value;
        #For one diffusing species
        GDiff = f0*np.exp(-x/tb)
        return GDiff

    def residual(self,param, x, data):
        """Calculates the difference between the data and the predicted model"""
        A = self.equation_(param, x)
        residuals = data-A
        return residuals
    def outputData(self):
        print 'The output data'
        #Find the object ref link
        
        

        corr_ratio = self.objId.CH0.shape[1]/self.objId.spatialBin
        #Fix the data with the correction function.
        for i in range(0, self.objId.CH0.shape[1]):
            inFn = self.objId.CH0[:,i]
            self.objId.CH0_pc[:,i] = self.apply_corr_fn(inFn,corr_ratio)
            
        #Save the data to carpets.
        if self.objId.numOfCH == 1:
            a,b,c,d = self.objId.calculateCarpet(self.objId.CH0_pc,None)
        elif self.objId.numOfCH == 2:
            for i in range(0, self.objId.CH1.shape[1]):
                inFn = self.objId.CH1[:,i]
                self.objId.CH1_pc[:,i] = self.apply_corr_fn(inFn,corr_ratio)
            a,b,c,d = self.objId.calculateCarpet(self.objId.CH0_pc,self.objId.CH1_pc)
        
        self.objId.corrArrScale_pc = a
        self.objId.AutoCorr_carpetCH0_pc = b
        self.objId.AutoCorr_carpetCH1_pc = c
        self.objId.CrossCorr_carpet01_pc = d
        self.objId.bleachCorr = True
        self.win_obj.bleachCorr_check_box.setChecked(True)

    def plotData(self):
        self.plt1.cla()
        
        #Calculate the total integral
        totalFn = np.sum(self.objId.CH0, 1).astype(np.float64)
        #Plot 1 in 10 pixels from the Gasussian.
        self.plt1.plot(range(0,totalFn.shape[0],10) ,totalFn[0::10],'blue')
        #If plotting with correction:
        if self.corrFn == True:
            
            #Learns the fit.
            self.weightings,  self.learn_f0 = self.learn_corr_fn(totalFn)
            out_total_fn = self.apply_corr_fn(totalFn,1)
            
            self.plt1.plot(range(0,out_total_fn.shape[0],10) ,out_total_fn[0::10], 'green')
            self.plt1.plot(range(0,out_total_fn.shape[0],10) ,self.weightings[0::10], 'red')
            
            
            self.plt1.set_ylim(bottom=0)

        
        if self.objId.numOfCH == 2:
            self.plt2.cla()
            #Calculate the total integral
            totalFn = np.sum(self.objId.CH1, 1).astype(np.float64)
            #Plot 1 in 10 pixels from the Gasussian.
            self.plt2.plot(range(0,totalFn.shape[0],10) ,totalFn[0::10],'blue')
            #If plotting with correction:
            if self.corrFn == True:
                
                #Learns the fit.
                self.weightings,  self.learn_f0 = self.learn_corr_fn(totalFn)
                out_total_fn = self.apply_corr_fn(totalFn,1)
                
                self.plt2.plot(range(0,out_total_fn.shape[0],10) ,out_total_fn[0::10], 'green')
                self.plt2.plot(range(0,out_total_fn.shape[0],10) ,self.weightings[0::10], 'red')
                
                
                self.plt2.set_ylim(bottom=0)

        self.canvas1.draw()

    def clicked(self):
        print 's'