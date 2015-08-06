from PyQt4 import QtGui, QtCore
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.lines as lines
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
from matplotlib.widgets import Slider
from scorrelation_objects import scanObject, autocorrelate

class bleachCorr2(QtGui.QMainWindow):
    def __init__(self,par_obj,win_obj):
        QtGui.QMainWindow.__init__(self)
        #self.fileArray = fileArray
        #self.create_main_frame()
        self.par_obj = par_obj
        self.win_obj = win_obj
        self.corrFn = False
        self.duration_combo_idx = 0
        
        

    def create_main_frame(self):
        for objId in self.par_obj.objectRef:
            if(objId.cb.isChecked() == True):
                self.objId=objId
                break;
        
        self.duration_array = [self.objId.num_of_lines*self.objId.deltat/1000, 4.000, 3.000,2.500,2.000, 1.500,1.000,0.5000,0.2500, 0.1250, 0.0625]
        self.corrFn = False      
        #self.trace_idx = self.par_obj.clickedS1

        page = QtGui.QWidget()        
        hbox_main = QtGui.QHBoxLayout()
        vbox1 = QtGui.QVBoxLayout()
        vbox0 = QtGui.QVBoxLayout()
        self.setWindowTitle("Bleach correction method 2: (local averaging)")
        self.figure1 = plt.figure(figsize=(10,8))
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        #self.canvas1 = FigureCanvas(self.figure1)
        
        self.figure1.patch.set_facecolor('white')
        self.canvas1 = FigureCanvas(self.figure1)

        
        
        
        self.plt1 = self.figure1.add_subplot(3,1,3)
        self.plt2 = self.figure1.add_subplot(3,1,2)
        self.plt3 = self.figure1.add_subplot(3,1,1)
        


        

        self.plt1.set_title('Intensity Time Trace')
        self.plt1.set_ylabel('Number of photons', fontsize=12)
        self.plt1.set_xlabel('Time (ms)', fontsize=12)

        self.plt2.set_title('Preview Different Window Sizes')
        self.plt2.set_ylabel('Correlation')
        self.plt2.set_xlabel('Time (ms)')


        cid = self.canvas1.mpl_connect('button_press_event', self.onclick)


            
        #line, = self.plt2.plot([0], [0])  # empty line
        #linebuilder = LineBuilder(line)
        carp_pix_sel_txt = QtGui.QLabel('Select carpet column pixel: ')


        self.carp_pix_sel = QtGui.QSpinBox()
        self.carp_pix_sel.setRange(0,self.win_obj.carpet_img.shape[0]);

        
        self.sel_channel = QtGui.QComboBox()
        self.sel_channel.addItem('CH0')
        if self.objId.numOfCH == 2:
            self.sel_channel.addItem('CH1')

        self.sel_channel.currentIndexChanged[int].connect(self.redraw_carpet)

        
        if self.win_obj.carpetDisplay == 1:
            self.sel_channel.setCurrentIndex(1)

        self.duration_combo = QtGui.QComboBox()
        self.duration_combo.addItem("full")
        self.duration_combo.addItem("4.0 s")
        self.duration_combo.addItem("3.0 s")
        self.duration_combo.addItem("2.5 s")
        self.duration_combo.addItem("2.0 s")
        self.duration_combo.addItem("1.5 s")
        self.duration_combo.addItem("1.0 s")
        self.duration_combo.addItem("0.5 s")
        self.duration_combo.addItem("0.25 s")
        self.duration_combo.addItem("0.1250 s")
        self.duration_combo.addItem("0.0625 s")
        
        
        
        self.duration_combo.setCurrentIndex(self.duration_combo_idx)
        
        
        
        
        
        self.duration = self.duration_array[0]
        self.duration_combo.activated[str].connect(self.duration_activated)
        

        self.preview_selection_btn = QtGui.QPushButton('Preview different intervals')
        self.preview_selection_btn.clicked.connect(self.preview_selection_fn)

        sel_time_window_size = QtGui.QLabel("Select time interval length")

        self.export_trace_btn = QtGui.QPushButton('Apply to Data')
        self.vbox2 = QtGui.QHBoxLayout()
        
        self.export_trace_btn.clicked.connect(self.outputData)
        
        self.carp_pix_sel.valueChanged[int].connect(self.line_redraw)

        hbox_main.addLayout(vbox0)
        hbox_main.addLayout(vbox1)
        vbox0.addWidget(self.sel_channel)
        vbox0.addWidget(carp_pix_sel_txt)
        vbox0.addWidget(self.carp_pix_sel)
        vbox0.addLayout(self.vbox2)
        vbox0.addWidget(self.preview_selection_btn)
        vbox0.addWidget(sel_time_window_size)
        vbox0.addWidget(self.duration_combo)
        vbox0.addWidget(self.export_trace_btn)
        vbox0.addStretch();
        vbox1.addWidget(self.canvas1)
        
        self.figure1.subplots_adjust(left=0.1, bottom=0.1, right=0.8, top=0.95, wspace=0.2, hspace=0.6)
        page.setLayout(hbox_main)
        self.setCentralWidget(page)
        self.show()
        self.plotData()
        self.redraw_carpet()
    def redraw_carpet(self):
        """To make sure """
        self.objId.bleachCorr1_checked = False
        self.objId.bleachCorr2_checked = False

        if self.sel_channel.currentIndex() == 1:
            self.win_obj.CH1AutoFn()
        else:
            self.win_obj.CH0AutoFn()
        self.plt3.set_xlabel('Time (ms)', fontsize=12)
        self.plt3.set_ylabel('Column pixel',fontsize=12)
        self.plt3.set_xscale('log')
        
        self.plt3.set_title('Correlation Carpet Preview')
        self.plt3.imshow(self.win_obj.carpet_img,extent=[self.objId.corrArrScale[0],self.objId.corrArrScale[-1],0,self.win_obj.carpet_img.shape[0]],interpolation ='nearest',picker=5)
        self.canvas1.draw()

    def line_redraw(self,value):
        try: 
            self.line.remove()
        except:
            pass
        self.line = self.plt3.axhline(value,color='black')
        self.canvas1.draw()

    def onclick(self,event):
            if event.inaxes == self.plt3:
                try: 
                    self.line.remove()
                except:
                    pass
                self.line = self.plt3.axhline(event.ydata,color='black')
                self.canvas1.draw()
                self.carp_pix_sel.setValue(int(event.ydata))
                

    def duration_activated(self,text):
            for i in range(0,self.duration_array.__len__()):
                if text ==  str(self.duration_array[i])+' s':
                    self.duration = self.duration_array[i]
                if text == str('full'):
                    self.duration = self.objId.num_of_lines
            

   
    def preview_selection_fn(self):
        
        start_x = 0
        
        self.plt2.clear()
        self.plt2.set_title('Preview Different Window Sizes')
        self.plt2.set_ylabel('Correlation')
        self.plt2.set_xlabel('Time (ms)')
        label_array = []
        for bit in self.duration_array:
            num_of_lines  = int(np.ceil((bit)/(self.objId.deltat/1000)))
            
            
            if num_of_lines%2 == 1:
                num_of_lines -= 1

            if num_of_lines< 2*self.objId.m:
                    continue;
            
            column_number = self.carp_pix_sel.value()
            if self.sel_channel.currentIndex() == 1:
                FT = self.objId.CH1[:,column_number]
            else: 
                FT = self.objId.CH0[:,column_number]

            

            k = int(np.floor(np.log2(num_of_lines/self.objId.m)))

            lenG = np.int(np.floor(self.objId.m + k*self.objId.m/2))

            out_all = np.zeros((lenG,1+np.ceil((FT.__len__()-num_of_lines)/num_of_lines)))
            c = 0
            
            for stx in range(start_x,FT.__len__()-num_of_lines+1,num_of_lines):
                
                

                out = autocorrelate(FT[stx:stx+num_of_lines].astype(np.float64),m=self.objId.m, deltat=self.objId.deltat, normalize=True,copy=True, dtype=None)
                #if out.shape[0] != out_all.shape[0]:
                #    out_all =  np.zeros((out.shape[0],1+np.ceil((FT.__len__()-num_of_lines)/num_of_lines)))
                out_all[:,c] = out[:,1]
                c += 1

            
            self.plt2.semilogx(out[:,0],np.average(out_all,1))
            label_array.append(bit)
            
        
        fontP = FontProperties()
        fontP.set_size('small')

        self.plt2.legend(np.round(label_array,3), loc="upper left", prop = fontP,bbox_to_anchor=(1.0,1.0))
        self.canvas1.draw()


        
                    

    def outputData(self):
        start_x = 0
        
        self.duration_combo_idx = self.duration_combo.currentIndex()
        if  self.duration_combo_idx >0:
            num_of_lines  = int(np.ceil((self.duration)/(self.objId.deltat/1000)))
            
            if num_of_lines%2 == 1:
                num_of_lines -= 1

            k = int(np.floor(np.log2(num_of_lines/self.objId.m)))
            lenG = np.int(np.floor(self.objId.m + k*self.objId.m/2))

            mar = int((self.objId.spatialBin-1)/2)
            AC_all_CH0 = np.zeros((lenG,self.objId.CH0.shape[1]-(2*mar),1+np.ceil(self.objId.CH0.shape[0]-num_of_lines)/num_of_lines))
            if self.objId.numOfCH==2:
                AC_all_CH1  = np.zeros((AC_all_CH0.shape))
                CC_all_CH01 = np.zeros((AC_all_CH0.shape))
            
            c = 0
            for stx in range(start_x,self.objId.CH0.shape[0]-num_of_lines+1,num_of_lines):
                #Function which calculates the correlation carpet.
                if self.objId.numOfCH==1:
                    self.objId.corrArrScale_pc, AC_carCH0, ap, aq = self.objId.calc_carpet(self.objId.CH0[stx:stx+num_of_lines,:],None,lenG)
                    AC_all_CH0[:,:,c] = AC_carCH0


                elif self.objId.numOfCH==2:
                    self.objId.corrArrScale_pc, AC_carCH0, AC_carCH1, CC_carCH01= self.objId.calc_carpet(self.objId.CH0[stx:stx+num_of_lines,:],self.objId.CH1[stx:stx+num_of_lines,:],lenG)
                    AC_all_CH0[:,:,c]  = AC_carCH0
                    AC_all_CH1[:,:,c]  = AC_carCH1
                    CC_all_CH01[:,:,c] = CC_carCH01
                
                c = c + 1

            
            #Calculate average carpet for output.
            self.objId.AutoCorr_carpetCH0_pc = np.average(AC_all_CH0,2)
            
            
            if self.objId.numOfCH == 2:
                self.objId.AutoCorr_carpetCH1_pc = np.average(AC_all_CH1,2)
                self.objId.CrossCorr_carpet01_pc = np.average(CC_all_CH01,2)
        else:
            #If full is selected, just defualt to normal carpet.
            self.objId.AutoCorr_carpetCH0_pc = self.objId.AutoCorr_carpetCH0
            self.objId.corrArrScale_pc =  self.objId.corrArrScale
            if self.objId.numOfCH == 2:
                self.objId.AutoCorr_carpetCH1_pc = self.objId.AutoCorr_carpetCH1
                self.objId.CrossCorr_carpet01_pc = self.objId.CrossCorr_carpet01


        
        #Applies to data and forgets old settings.
        self.objId.bleachCorr1 = False
        self.objId.bleachCorr2 = True
        self.win_obj.bleachCorr1_checked = False
        self.win_obj.bleachCorr2_checked = False
        
        #Lets the user change channel.
        if self.sel_channel.currentIndex() == 1:
            self.win_obj.carpetDisplay = 1
        else:
            self.win_obj.carpetDisplay = 0
        self.win_obj.bleachCorr2fn()
        
        #Updates buttons on main gui.
        self.win_obj.bleachCorr1_on_off.setText('OFF')
        self.win_obj.bleachCorr1_on_off.setStyleSheet(" color: red");
        self.win_obj.bleachCorr2_on_off.setText('ON')
        self.win_obj.bleachCorr2_on_off.setStyleSheet(" color: green");

        #Plots the carpet internally.
        self.plt3.clear()
        self.plt3.set_title('Correlation Carpet Preview')
        self.plt3.set_xlabel('Time (ms)', fontsize=12)
        self.plt3.set_ylabel('Column pixel',fontsize=12)
        self.plt3.set_xscale('log')
        
        self.plt3.imshow(self.win_obj.carpet_img,extent=[self.objId.corrArrScale[0],self.objId.corrArrScale[-1],0,self.win_obj.carpet_img.shape[0]],interpolation ='nearest')
        self.plotData()
        self.canvas1.draw()

        
    def plotData(self):
        self.plt1.clear()
        start_x = 0
        #Calculate the total integral
        num_of_lines  = int(np.ceil((self.duration)/(self.objId.deltat/1000)))

        if self.sel_channel.currentIndex() ==1:
            totalFn = np.sum(self.objId.CH1, 1).astype(np.float64)
        else:
            totalFn = np.sum(self.objId.CH0, 1).astype(np.float64)
        #Plot 1 in 10 pixels from the Gasussian.
        if self.duration_combo_idx >0:
            c = 0
            for stx in range(start_x,self.objId.CH0.shape[0]-num_of_lines+1,num_of_lines):
                c =c+1
                if c%2==1:
                    color = 'blue'
                else:
                    color = 'black'
                self.plt1.plot(np.arange(stx,stx+num_of_lines,10)*self.objId.deltat ,totalFn[stx:stx+num_of_lines:10],color=color)
        else:
            self.plt1.plot(np.arange(0,totalFn.shape[0],10)*self.objId.deltat ,totalFn[::10],color='blue')
        
        #If plotting with correction:
        self.plt1.set_title('Intensity Time Trace')
        self.plt1.set_ylabel('Intensity count')
        self.plt1.set_xlabel('Time (ms)')
        self.canvas1.draw()

    







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
            self.plt1.plot(np.arange(0,totalFn.shape[0],10)*self.objId.deltat ,totalFn[0::10],'red')
            
        
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
    def __init__(self,par_obj,win_obj):
        QtGui.QMainWindow.__init__(self)
        #self.fileArray = fileArray
        #self.create_main_frame()
        self.par_obj = par_obj
        self.win_obj = win_obj
        self.corrFn = False
        

    def create_main_frame(self):
        for objId in self.par_obj.objectRef:
            if(objId.cb.isChecked() == True):
                self.objId=objId
                break;
        self.corrFn = False      
        #self.trace_idx = self.par_obj.clickedS1

        page = QtGui.QWidget()        
        hbox_main = QtGui.QHBoxLayout()
        vbox1 = QtGui.QVBoxLayout()
        vbox0 = QtGui.QVBoxLayout()
        self.setWindowTitle("Bleach correction")
        self.figure1 = plt.figure(figsize=(10,4))
        self.figure1.subplots_adjust(left=0.1, bottom=0.2, right=0.95, top=0.90, wspace=0.3, hspace=0.2)
        
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
        self.export_trace_btn.setEnabled(False)
        self.vbox2 = QtGui.QHBoxLayout()
        self.apply_corr_btn = QtGui.QPushButton('Generate Correction')
        
        
        self.export_trace_btn.clicked.connect(self.outputData)
        self.apply_corr_btn.clicked.connect(self.plot_corrFn)
        
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
        self.export_trace_btn.setEnabled(True)
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
        
        #Find the object ref link
        
        

        corr_ratio = self.objId.CH0.shape[1]/self.objId.spatialBin
        #Fix the data with the correction function.
        for i in range(0, self.objId.CH0.shape[1]):
            inFn = self.objId.CH0[:,i]
            self.objId.CH0_pc[:,i] = self.apply_corr_fn(inFn,corr_ratio)
            
        #Save the data to carpets.
        if self.objId.numOfCH == 1:
            a,b,c,d = self.objId.calc_carpet(self.objId.CH0_pc,None,self.objId.lenG)
        elif self.objId.numOfCH == 2:
            for i in range(0, self.objId.CH1.shape[1]):
                inFn = self.objId.CH1[:,i]
                self.objId.CH1_pc[:,i] = self.apply_corr_fn(inFn,corr_ratio)
            a,b,c,d = self.objId.calc_carpet(self.objId.CH0_pc,self.objId.CH1_pc,self.objId.lenG)
        
        self.objId.corrArrScale_pc = a
        self.objId.AutoCorr_carpetCH0_pc = b
        self.objId.AutoCorr_carpetCH1_pc = c
        self.objId.CrossCorr_carpet01_pc = d
        

        self.objId.bleachCorr1 = True
        self.objId.bleachCorr2 = False
        self.win_obj.bleachCorr1_checked = False
        self.win_obj.bleachCorr2_checked = False
        self.win_obj.bleachCorr1fn()
        self.win_obj.bleachCorr1_on_off.setText('ON')
        self.win_obj.bleachCorr1_on_off.setStyleSheet(" color: green");
        self.win_obj.bleachCorr2_on_off.setText('OFF')
        self.win_obj.bleachCorr2_on_off.setStyleSheet(" color: red");

    def plotData(self):
        self.plt1.cla()
        self.plt1.set_title('Intensity Time Trace CH0')
        self.plt1.set_ylabel('Intensity Counts')
        self.plt1.set_xlabel('Time (ms)')
        
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
            self.plt2.set_title('Intensity Time Trace CH1')
            self.plt2.set_ylabel('Intensity Counts')
            self.plt2.set_xlabel('Time (ms)')
            #Calculate the total integral
            totalFn = np.sum(self.objId.CH1, 1).astype(np.float64)
            #Plot 1 in 10 pixels from the Gasussian.
            self.plt2.plot(range(0,totalFn.shape[0],10) ,totalFn[0::10],'grey')
            #If plotting with correction:
            if self.corrFn == True:
                
                #Learns the fit.
                self.weightings,  self.learn_f0 = self.learn_corr_fn(totalFn)
                out_total_fn = self.apply_corr_fn(totalFn,1)
                
                self.plt2.plot(range(0,out_total_fn.shape[0],10) ,out_total_fn[0::10], 'green')
                self.plt2.plot(range(0,out_total_fn.shape[0],10) ,self.weightings[0::10], 'red')
                
                
                self.plt2.set_ylim(bottom=0)

        self.canvas1.draw()
