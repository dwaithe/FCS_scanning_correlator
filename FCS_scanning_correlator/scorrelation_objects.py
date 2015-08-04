import sys, os
import numpy as np
import cPickle as pickle
from scorrelation_methods import *
import csv
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
from fitting_methods import equation_
import time
import copy

class scanObject():
    #This is the class which you store the variables in.
    def __init__(self,filepath,parObj,imDataDesc,imDataStore,start_pt,end_pt):
        #Binning window for decay function
       
        #Parameters for auto-correlation and cross-correlation.
        self.start_pt = start_pt
        self.end_pt = end_pt

        self.parentId = None
        
        self.filepath = str(filepath)
        self.parObj = parObj
        self.nameAndExt = os.path.basename(self.filepath).split('.')
        
        self.file_name = self.nameAndExt[0]
        self.ext = self.nameAndExt[-1]
        self.parObj.data.append(filepath);
        self.parObj.objectRef.append(self)

        self.unqID = self.parObj.numOfLoaded
        self.type = 'scan ' +str(self.unqID)
        self.objId1 = None
        self.objId2 = None
        self.objId3 = None
        self.objId4 = None
        self.objId5 = [];
        

        self.imDataDesc = imDataDesc
        self.imDataStore = imDataStore
        self.plotOn = True;

        self.pane = 0;
        self.maxPane = 0;
        self.bleachCorr1 = False
        #self.bleachCorr1_checked = False
        #self.bleachCorr2_checked = False
        self.bleachCorr2 = False
        
        
        self.processData()
        
        self.parObj.numOfLoaded = self.parObj.numOfLoaded+1
        
        #self.parObj.updateCombo()
        #self.parObj.cbx.setCurrentIndex(self.parObj.label.numOfLoaded-1)
        
    def correctBleach(self):
        print correctingBleach
        
    def calc_carpet(self, photonCarpetCH0,photonCarpetCH1,lenG):
            
            #For making a correlation carpet.
            CH0arr =[]
            CH1arr =[]
            corrArrCH0 =[]
            corrArrCH1 = []
            corrArrCC=[]
            self.kcountCH0 = []
            self.kcountCH1 = []
            self.numberNandBCH0 =[]
            self.numberNandBCH1 =[]
            self.brightnessNandBCH0 =[]
            self.brightnessNandBCH1 =[]

            numOfOp = photonCarpetCH0.shape[1]
            
            mar = int((self.spatialBin-1)/2)

            
            
            for i in range(mar,numOfOp-mar):
                #The spatial bin is either side of the column
                umar = mar
                lmar = umar
                if self.spatialBin ==1:
                    lmar = 0
                    umar = 1
                inFnCH0 = np.sum(photonCarpetCH0[:,i-lmar:i+umar],1).astype(np.float64)
                if self.numOfCH ==2:
                    inFnCH1 = np.sum(photonCarpetCH1[:,i-lmar:i+umar],1).astype(np.float64)
                
                #nlines = self.num_of_lines
                start_x = 0
                #Correlation applied to each column of the correlation carpet.
                if np.sum(np.array(inFnCH0))>0:

                    
                    AC0 = autocorrelate(np.array(inFnCH0), m=self.m, deltat=self.deltat, normalize=True,copy=True, dtype=None)
                    

                    corrArrScale = AC0[:,0]
                else:

                    AC0 = np.zeros((lenG,2))
                    
                
                #Calculate number of counts

                int_time = 50
                out = []
                for i in range(1,int(np.ceil((inFnCH0.shape[0]/int_time)))):
                    out.append(np.sum(inFnCH0[int_time*(i-1):int_time*i]))

                raw_count = np.average(out) #This is the unnormalised intensity count for int_time duration (the first moment)
                var_count = np.var(out) #This is the second moment the variance

                


                kcount = raw_count/(int_time*self.dwell_time*self.spatialBin) #Hz dwell time is important here, not line time.
                self.kcountCH0.append(kcount/1000)#KHz

                #Calculate the brightness and number using the moments.
                self.brightnessNandBCH0.append(((var_count -raw_count)/(raw_count))/(int_time*self.dwell_time*self.spatialBin)/1000)
                self.numberNandBCH0.append(raw_count**2/(var_count-raw_count))
                
                
                corrArrCH0.append(AC0)
                
                if self.numOfCH ==2:
                    AC1 = autocorrelate(np.array(inFnCH1), m=self.m, deltat=self.deltat, normalize=True,copy=True, dtype=None)
                    CC01 = correlate(np.array(inFnCH0),np.array(inFnCH1), m=self.m, deltat=self.deltat, normalize=True,copy=True, dtype=None)
                    corrArrCH1.append(AC1)
                    corrArrCC.append(CC01)
                    
                    out = []
                    for i in range(1,int(np.ceil((inFnCH1.shape[0]/int_time)))):
                        out.append(np.sum(inFnCH1[int_time*(i-1):int_time*i]))

                    raw_count = np.average(out) #This is the unnormalised intensity count for int_time duration
                    kcount = raw_count/(int_time*self.dwell_time*self.spatialBin)
                    var_count = np.var(out)

                    self.brightnessNandBCH1.append(((var_count -raw_count)/(raw_count))/(int_time*self.dwell_time*self.spatialBin)/1000)
                    self.numberNandBCH1.append(raw_count**2/(var_count-raw_count))
                
                    
                    self.kcountCH1.append(kcount)#average count per window. Need to convert to second.
                
            #Create ouput image.
            AutoCorr_carpetCH0 = np.zeros((lenG,corrArrCH0.__len__()))
            AutoCorr_carpetCH1 = None
            CrossCorr_carpet01 = None
            
            if self.numOfCH ==2:
                AutoCorr_carpetCH1 = np.zeros((lenG,corrArrCH1.__len__()))
                CrossCorr_carpet01 = np.zeros((lenG,corrArrCC.__len__()))
            
                    
            
            #Fill in the images with the correlation distributions.
            for b in range(0,corrArrCH0.__len__()):
                
                    AutoCorr_carpetCH0[:,b] = corrArrCH0[b][:,1]
            if self.numOfCH ==2:
                for b in range(0,corrArrCH1.__len__()):
                    AutoCorr_carpetCH1[:,b] = corrArrCH1[b][:,1]
                    CrossCorr_carpet01[:,b] = corrArrCC[b][:,1]    

            return corrArrScale, AutoCorr_carpetCH0, AutoCorr_carpetCH1, CrossCorr_carpet01
        

    def processData(self):
        #self.deltat=float(self.parObj.DeltatEdit.text())
        self.m = self.parObj.m #int(self.parObj.mEdit.text())
        self.spatialBin = self.parObj.spatialBin #int(self.parObj.spatialBinEdit.text())
        #self.photonCountBin = int(self.parObj.photonCountEdit.text())
        
        if self.ext == 'tif' or self.ext == 'tiff':
            
            self.dimSize = self.imDataStore.shape
            self.name = str(self.filepath).split('/')[-1]
            self.deltat = self.imDataDesc[0]
            self.dwell_time = self.imDataDesc[1]
            
            self.CH0 = np.array(self.imDataStore).astype(np.float64)
            if self.end_pt != 0:
                self.CH0 = np.array(self.imDataStore[self.start_pt:self.end_pt,:]).astype(np.float64)
            self.CH0_pc = np.zeros((self.CH0.shape))
            self.numOfCH =1
        elif self.ext == 'lsm':
            #For lsm files the dimensions can vary.
            if self.imDataStore.shape.__len__() > 2:
                self.dimSize = [self.imDataStore.shape[1],self.imDataStore.shape[2]]
                self.numOfCH = 2
            else:
                self.dimSize = [self.imDataStore.shape[0],self.imDataStore.shape[1]]
                self.numOfCH = 1
            self.name = str(self.filepath).split('/')[-1]
            self.deltat = self.imDataDesc[0]
            self.dwell_time = self.imDataDesc[1]
            
            if self.imDataStore.shape.__len__() > 2:
                self.CH0 = np.array(self.imDataStore[0,:,:]).astype(np.float64)
                if self.end_pt != 0:
                    self.CH0 = np.array(self.imDataStore[0,self.start_pt:self.end_pt,:]).astype(np.float64)
            else:
                self.CH0 = np.array(self.imDataStore[:,:]).astype(np.float64)
                if self.end_pt != 0:
                    self.CH0 = np.array(self.imDataStore[self.start_pt:self.end_pt,:]).astype(np.float64)
            #print 'self.CH0',self.CH0.shape
            #print 'self.CH0',np.sum(self.CH0)
            self.CH0_pc = np.zeros((self.CH0.shape))
            
            if self.numOfCH ==2:
                self.CH1 = np.array(self.imDataStore[1,:,:]).astype(np.float64)
                if self.end_pt != 0:
                    self.CH1 = np.array(self.imDataStore[1,self.start_pt:self.end_pt,:]).astype(np.float64)
                self.CH1_pc = np.zeros((self.CH1.shape))

           
        elif self.ext == 'lif':
    
            self.name = self.imDataDesc[7]
            self.dwell_time = float(self.imDataDesc[6])
            
            self.memSize = int(self.imDataDesc[1])
            self.LUTName = self.imDataDesc[2]
            self.dimSize = [int(self.imDataDesc[3][0]),int(self.imDataDesc[3][1]),int(self.imDataDesc[3][2])]
            #For display we divide image into sections or panes.
            
            #Convert to ms, default is seconds.
            self.deltat  = float(self.imDataDesc[4][0])*1000
            tempList0 =[];
            tempList1 =[];

            self.numOfCH = self.LUTName.__len__();

            #Single channel is simple to reshape from pages.
            if self.numOfCH == 1:
                    
                    self.CH0 = np.array(self.imDataStore).reshape(self.dimSize[1]*self.dimSize[2],self.dimSize[0])
                    #This is for the crop function
                    if self.end_pt != 0:
                        self.CH0 = self.CH0[self.start_pt:self.end_pt,:]
                    self.CH0_pc = np.zeros((self.CH0.shape))
                    
                    
                    #If more than one channel, have to rearrange data before reshapeing.
            elif self.numOfCH ==2:
                    
                    unit = int(self.dimSize[1]*self.dimSize[0])
                    for b in range(0,self.dimSize[2]):
                        i=b*2
                        tempList0.extend(self.imDataStore[int(unit*i):int(unit*(i+1))])
                        tempList1.extend(self.imDataStore[int(unit*(i+1)):int(unit*(i+2))])

                    self.CH0 = np.array(tempList0).reshape(self.dimSize[1]*self.dimSize[2],self.dimSize[0])
                    #This is for the crop function
                    if self.end_pt != 0:
                        self.CH0 = self.CH0[self.start_pt:self.end_pt,:]
                    
                    self.CH1 = np.array(tempList1).reshape(self.dimSize[1]*self.dimSize[2],self.dimSize[0])
                    #This is for the crop function.
                    if self.end_pt != 0:
                        self.CH1 = self.CH1[self.start_pt:self.end_pt,:]
                    
                    self.CH0_pc = np.zeros((self.CH0.shape))
                    self.CH1_pc = np.zeros((self.CH1.shape))
                    
            #import pickle 
            #pickle.dump(self.CH0,open("pickle1","wb"))      

            
            self.deltat = float(self.deltat);

        
        self.maxPane= np.floor(float(self.dimSize[1])/((float(self.CH0.shape[1]))/64)*150)
        #pickle.dump( self.CH0, open( "save.p", "wb" ) )
        self.CH0_arraySum = np.sum(self.CH0[:,:],1).astype(np.float64)
        self.CH0_arrayColSum = np.sum(self.CH0[:,:],0).astype(np.float64)
        self.maxCountCH0 = np.max(self.CH0_arraySum)
        
        #CH0auto = autocorrelate(self.CH0_arraySum, m=self.m, deltat=self.deltat, normalize=True, copy=True, dtype=None)
        if self.numOfCH ==2:
            self.CH1_arraySum = np.sum(self.CH1[:,:],1).astype(np.float64)
            self.CH1_arrayColSum = np.sum(self.CH1[:,:],0).astype(np.float64)
            self.maxCountCH1 = np.max(self.CH1_arraySum)
        

        #Colour assigned to file.
        self.color =self.parObj.colors[self.unqID % len(self.parObj.colors)]
        start_x = 0
        self.num_of_lines  = self.CH0.shape[0]
        if self.num_of_lines%2 == 1:
            self.num_of_lines -= 1

        k = int(np.floor(np.log2(self.num_of_lines/self.m)))
        self.lenG = np.int(np.floor(self.m + k*self.m/2))
        
        mar = int((self.spatialBin-1)/2)


        AC_all_CH0 = np.zeros((np.int(np.floor(self.m + k*self.m/2)),self.CH0.shape[1]-(2*mar),1+np.ceil(self.CH0.shape[0]-self.num_of_lines)/self.num_of_lines))
        if self.numOfCH==2:
            AC_all_CH1  = np.zeros((AC_all_CH0.shape))
            CC_all_CH01 = np.zeros((AC_all_CH0.shape))
        
        c = 0
        for stx in range(start_x,self.CH0.shape[0]-self.num_of_lines+1,self.num_of_lines):
            #Function which calculates the correlation carpet.
            if self.numOfCH==1:
                self.corrArrScale, AC_carCH0, ap, aq = self.calc_carpet(self.CH0[stx:stx+self.num_of_lines,:],None,self.lenG)
                AC_all_CH0[:,:,c] = AC_carCH0


            elif self.numOfCH==2:
                self.corrArrScale, AC_carCH0, AC_carCH1, CC_carCH01 = self.calc_carpet(self.CH0[stx:stx+self.num_of_lines,:],self.CH1[stx:stx+self.num_of_lines,:],self.lenG)
                AC_all_CH0[:,:,c]  = AC_carCH0
                AC_all_CH1[:,:,c]  = AC_carCH1
                CC_all_CH01[:,:,c] = CC_carCH01
            
            c = c+1


        self.AutoCorr_carpetCH0 = np.average(AC_all_CH0,2)
        if self.numOfCH == 2:
            self.AutoCorr_carpetCH1 = np.average(AC_all_CH1,2)
            self.CrossCorr_carpet01 = np.average(CC_all_CH01,2)

        #Creates data for initial plot distribution.
        self.autoNorm = np.zeros((AC_all_CH0.shape[0],4,4))
        self.autoNorm[:,0,0] = np.average(AC_all_CH0,2)[:,0]
        if self.numOfCH == 2:
            self.autoNorm[:,1,1] = np.average(AC_all_CH1,2)[:,0]
            self.autoNorm[:,0,1] = np.average(CC_all_CH01,2)[:,0]



        self.autotime = self.corrArrScale


       
        
class corrObject():
    def __init__(self,filepath,parentFn):
        #the container for the object.
        self.parentFn = parentFn
        self.type = 'corrObject'
        self.filepath = str(filepath)
        self.nameAndExt = os.path.basename(self.filepath).split('.')
        self.name = self.nameAndExt[0]
        self.ext = self.nameAndExt[-1]
        self.autoNorm=[]
        self.autotime=[]
        self.model_autoNorm =[]
        self.model_autotime = []
        self.datalen= []
        self.objId = self;
        self.param = []
        self.goodFit = True
        self.fitted = False
        self.checked = False
        self.toFit = False
       
        #main.data.append(filepath);
        #The master data object reference 
        #main.corrObjectRef.append(self)
        #The id in terms of how many things are loaded.
        #self.unqID = main.label.numOfLoaded;
        #main.label.numOfLoaded = main.label.numOfLoaded+1
    def prepare_for_fit(self):
        if self.parentFn.ch_check_ch0.isChecked() == True and self.ch_type == 0:
            self.toFit = True
        if self.parentFn.ch_check_ch1.isChecked() == True and self.ch_type == 1:
            self.toFit = True
            
        if self.parentFn.ch_check_ch01.isChecked() == True and self.ch_type == 2:
            self.toFit = True
        if self.parentFn.ch_check_ch10.isChecked() == True and self.ch_type == 3:
            self.toFit = True
        #self.parentFn.modelFitSel.clear()
        #for objId in self.parentFn.objIdArr:
         #   if objId.toFit == True:
          #      self.parentFn.modelFitSel.addItem(objId.name)
        self.parentFn.updateFitList()
    def residual(self, param, x, data,options):
    
        A = equation_(param, x,options)
        residuals = data-A
        return residuals
    def fitToParameters(self):
        self.parentFn.updateParamFirst()
        self.parentFn.updateTableFirst()
        self.parentFn.updateParamFirst()
        
        param = Parameters()
        #self.def_param.add('A1', value=1.0, min=0,max=1.0, vary=False)
        for art in self.param:
            
            if self.param[art]['to_show'] == True:
                param.add(art, value=float(self.param[art]['value']), min=float(self.param[art]['minv']) ,max=float(self.param[art]['maxv']), vary=self.param[art]['vary']);
                
        
        #Find the index of the nearest point in the scale.
        data = np.array(self.autoNorm).astype(np.float64).reshape(-1)
        scale = np.array(self.autotime).astype(np.float64).reshape(-1)
        indx_L = int(np.argmin(np.abs(scale -  self.parentFn.dr.xpos)))
        indx_R = int(np.argmin(np.abs(scale -  self.parentFn.dr1.xpos)))
        
        #Does the fitting.
        res = minimize(self.residual, param, args=(scale[indx_L:indx_R+1],data[indx_L:indx_R+1], self.parentFn.def_options))

        for art in self.param:
            if self.param[art]['to_show'] == True:
                self.param[art]['value'] = param[art].value
        #Extra parameters, which are not fit or inherited.
        self.param['N_FCS']['value'] = np.round(1/self.param['GN0']['value'],4)
        
        if self.ch_type != 2:
            #Are not calculated for cross-calculation.
            self.param['cpm']['value'] = np.round(self.kcount*self.param['GN0']['value'],2)
            self.param['N_mom']['value'] = np.round(float(self.numberNandB),4)
            self.param['bri']['value'] = np.round(float(self.brightnessNandB),2)
            
            #if self.siblings[1].fitted == True:
            #    self.param['ACAC']['value'] = np.round(float(self.param['GN0']['value'])/float(self.siblings[1].param['GN0']['value']),4)
            
            #try:
            #    self.param['ACCC']['value'] = np.round(float(self.param['GN0']['value'])/float(self.siblings[2].param['GN0']['value']),4)
            #except:
            #    pass
                        
            
        
        self.residualVar = res.residual
        output = fit_report(param)
        print 'residual',res.chisqr
        if(res.chisqr>0.05):
            print 'CAUTION DATA DID NOT FIT WELL CHI^2 >0.05',res.chisqr
            self.goodFit = False
        else:
            self.goodFit = True
        self.fitted = True
        self.chisqr = res.chisqr



        #Prepares the data for the output.
        rowArray =[];
        localTime = time.asctime( time.localtime(time.time()) )
        rowArray.append(str(self.name))  
        rowArray.append(str(localTime))
        rowArray.append(str(self.parentFn.diffModEqSel.currentText()))
        rowArray.append(str(self.parentFn.def_options['Diff_species']))
        rowArray.append(str(self.parentFn.tripModEqSel.currentText()))
        rowArray.append(str(self.parentFn.def_options['Triplet_species']))
        rowArray.append(str(self.parentFn.dimenModSel.currentText()))
        rowArray.append(str(scale[indx_L]))
        rowArray.append(str(scale[indx_R]))

        
        


        #Adds the fields which are stored in the parameters.
        for key, value in param.iteritems() :
            rowArray.append(str(value.value))
            rowArray.append(str(value.stderr))
            if key =='GN0':
                try:
                    rowArray.append(str(self.param['N_FCS']['value']))
                    if self.ch_type !=2:
                        rowArray.append(str(self.param['cpm']['value']))
                    else:
                        rowArray.append('')
                except:
                    rowArray.append(str(0))
        #Adds non-fit parameters.
        try:
            rowArray.append(str(np.round(float(self.numberNandB),5)))
            rowArray.append(str(np.round(float(self.brightnessNandB),5)))

        except:
           pass

        self.rowText = rowArray

        self.parentFn.updateTableFirst();
        
        
        #Creates the output data from the fit.
        self.model_autoNorm = equation_(param, scale[indx_L:indx_R+1],self.parentFn.def_options)
        self.model_autotime = scale[indx_L:indx_R+1]
        self.parentFn.on_show()

        #self.parentFn.axes.plot(model_autotime,model_autoNorm, 'o-')
        #self.parentFn.canvas.draw();
    
    def load_from_file(self,channel):
        tscale = [];
        tdata = [];
        if self.ext == 'SIN':
            self.parentFn.objIdArr.append(self.objId)
            proceed = False
            
            for line in csv.reader(open(self.filepath, 'rb'),delimiter='\t'):
                
                if proceed ==True:
                    if line ==[]:
                        break;
                    
                    
                    tscale.append(float(line[0]))
                    tdata.append(float(line[channel+1]))
                else:
                  
                  if (str(line)  == "[\'[CorrelationFunction]\']"):
                    proceed = True;
            

            self.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
            self.autotime= np.array(tscale).astype(np.float64).reshape(-1)*1000
            
            self.name = self.name+'-CH'+str(channel)
            self.ch_type = channel;
            self.prepare_for_fit()


            self.param = copy.deepcopy(self.parentFn.def_param)
            self.parentFn.fill_series_list()
            
        
                    #Where we add the names.


        if self.ext == 'csv':
            
            self.parentFn.objIdArr.append(self)
            
            c = 0
            
            for line in csv.reader(open(self.filepath, 'rb')):
                if (c >0):
                    tscale.append(line[0])
                    tdata.append(line[1])
                c +=1;

            self.autoNorm= np.array(tdata).astype(np.float64).reshape(-1)
            self.autotime= np.array(tscale).astype(np.float64).reshape(-1)
            self.ch_type = 0
            self.datalen= len(tdata)
            self.objId.prepare_for_fit()

        



