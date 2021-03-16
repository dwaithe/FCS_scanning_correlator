import sys, os
import numpy as np
import _pickle as pickle
from scorrelation_methods import *
import csv
from lmfit import minimize, Parameters,report_fit,report_errors, fit_report
from focuspoint.fitting_methods.fitting_methods_SE import equation_
import time
import copy

class scanObject():
    #This is the class which you store the variables in.
    def __init__(self,filepath,parObj,imDataDesc,imDataStore,start_pt,end_pt, cmin=None,cmax=None):
        #Binning window for decay function
       
        
        #These settings are important if a carpet is reprocessed due to cropping.
        self.start_pt = int(start_pt)
        self.end_pt = int(end_pt)
        self.cmin = None
        self.cmax = None
        if cmin !=None and cmax !=None:
            self.cmin = int(cmin)
            self.cmax = int(cmax)
        

        #Parameters for auto-correlation and cross-correlation.
        self.parentId = None
        
        self.filepath = str(filepath)
        
        self.parObj = parObj
        self.nameAndExt = os.path.basename(self.filepath).split('.')
        self.file_name = self.nameAndExt[0]
        self.ext = self.nameAndExt[-1]
        #self.parObj.data.append(filepath);
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
        

        
    def calc_carpet(self, photonCarpetCH0,photonCarpetCH1,lenG):
            
            #For making a correlation carpet.
            CH0arr =[]
            CH1arr =[]
            corrArrCH0 =[]
            corrArrCH1 = []
            corrArrCC=[]
            kcountCH0 = []
            kcountCH1 = []
            numberNandBCH0 =[]
            numberNandBCH1 =[]
            brightnessNandBCH0 =[]
            brightnessNandBCH1 =[]
            signal_to_noiseCH0 = []
            signal_to_noiseCH1 = []
            CV = []
            
            numOfOps = photonCarpetCH0.shape[1]

            
            mar = int((self.spatialBin-1)/2)


            #Zero pixels are bad for many calculations. Here we check and replace with very small number.

            #photonCarpetCH0[photonCarpetCH0==0.0] = 1e-6
            #if self.numOfCH == 2:
             #   photonCarpetCH1[photonCarpetCH1==0.0] = 1e-6



            
            
            for i in range(mar,numOfOps-mar):
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
                sum_of_inFnCH0 = np.sum(np.array(inFnCH0))
                if sum_of_inFnCH0 > 0:

                    
                    AC0 = autocorrelate(np.array(inFnCH0), m=self.m, deltat=self.deltat, normalize=True,copy=True, dtype=None)
                    corrArrScale = AC0[:,0]
                    signal_to_noiseCH0.append(self.calc_signal_to_noise(inFnCH0,AC0))
                    
                
                    #Calculate number of counts

                    int_time = 50
                    out = []
                    for i in range(1,int(np.ceil((inFnCH0.shape[0]/int_time)))):
                        out.append(np.sum(inFnCH0[int_time*(i-1):int_time*i]))

                    raw_count = np.average(out) #This is the unnormalised intensity count for int_time duration (the first moment)
                    var_count = np.var(out) #This is the second moment the variance

                    

                    #Calculate the number of kcounts / Hz.
                    print(self.dwell_time)
                    kcount = raw_count/(int_time*self.dwell_time*self.spatialBin) #Hz dwell time is important here, not line time.
                    kcountCH0.append(kcount/1000)#KHz



                    #Calculate the brightness and number using the moments.
                    brightnessNandBCH0.append(((var_count -raw_count)/(raw_count))/(int_time*self.dwell_time*self.spatialBin)/1000)
                    
                    if (var_count-raw_count) == 0:
                        numberNandBCH0.append(0)
                    else:
                        numberNandBCH0.append(raw_count**2/(var_count-raw_count))
                else:

                    AC0 = np.zeros((lenG,2))
                    corrArrScale = AC0[:,0]
                    signal_to_noiseCH0.append(0)
                    kcountCH0.append(0)
                    brightnessNandBCH0.append(0)
                    numberNandBCH0.append(0)



                

                
                corrArrCH0.append(AC0)
                if self.numOfCH ==2:
                    #If there are two channels calculate the coincidence.
                    sum_of_inFnCH1 = np.sum(np.array(inFnCH1))
                    #This is only tested for lif files.
                    option = np.bincount((inFnCH0).astype(np.int64))
                    try:
                        scalefactor = np.diff(np.where(option > 0)[0])[0]
                    except:
                        scalefactor = 1
                    N1 = np.bincount((inFnCH0/scalefactor).astype(np.int64))
                    N2 = np.bincount((inFnCH1/scalefactor).astype(np.int64))
                    n = max(N1.shape[0],N2.shape[0])
                    NN1 = np.zeros(n)
                    NN2 = np.zeros(n)
                    NN1[:N1.shape[0]] = N1 
                    NN2[:N2.shape[0]] = N2 
                    N1 = NN1
                    N2 = NN2
                    
                    CV.append((np.sum(N1*N2)/(np.sum(N1)*np.sum(N2)))*n)
            
                    if sum_of_inFnCH1 > 0:

                        AC1 = autocorrelate(np.array(inFnCH1), m=self.m, deltat=self.deltat, normalize=True,copy=True, dtype=None)
                        CC01 = correlate(np.array(inFnCH0),np.array(inFnCH1), m=self.m, deltat=self.deltat, normalize=True,copy=True, dtype=None)
                        corrArrCH1.append(AC1)
                        corrArrCC.append(CC01)

                        signal_to_noiseCH1.append(self.calc_signal_to_noise(inFnCH1,AC1))
                        
                        out = []
                        for i in range(1,int(np.ceil((inFnCH1.shape[0]/int_time)))):
                            out.append(np.sum(inFnCH1[int_time*(i-1):int_time*i]))

                        raw_count = np.average(out) #This is the unnormalised intensity count for int_time duration
                        kcount = raw_count/(int_time*self.dwell_time*self.spatialBin)
                        var_count = np.var(out)

                        brightnessNandBCH1.append(((var_count -raw_count)/(raw_count))/(int_time*self.dwell_time*self.spatialBin)/1000)
                        numberNandBCH1.append(raw_count**2/(var_count-raw_count))
                        
                        kcountCH1.append(kcount/1000) #Khz
                    else:
                        AC1 = np.zeros((lenG,2))
                        CC01 = np.zeros((lenG,2))
                        corrArrCH1.append(AC1)
                        corrArrCC.append(CC01)
                        signal_to_noiseCH1.append(0)
                        brightnessNandBCH1.append(0)
                        numberNandBCH1.append(0)
                        kcountCH1.append(0)


                    #average count per window. Need to convert to second.
                
            #Create ouput image.
            AutoCorr_carpetCH0 = np.zeros((corrArrCH0[0][:,1].shape[0],corrArrCH0.__len__()))
            AutoCorr_carpetCH1 = None
            CrossCorr_carpet01 = None
            
            if self.numOfCH ==2:
                AutoCorr_carpetCH1 = np.zeros((corrArrCH0[0][:,1].shape[0],corrArrCH1.__len__()))
                CrossCorr_carpet01 = np.zeros((corrArrCH0[0][:,1].shape[0],corrArrCC.__len__()))
            
                    
            
            #Fill in the images with the correlation distributions.
            for b in range(0,corrArrCH0.__len__()):
                
                    AutoCorr_carpetCH0[:,b] = corrArrCH0[b][:,1]
            if self.numOfCH ==2:
                for b in range(0,corrArrCH1.__len__()):
                    AutoCorr_carpetCH1[:,b] = corrArrCH1[b][:,1]
                    CrossCorr_carpet01[:,b] = corrArrCC[b][:,1]    

            return corrArrScale, AutoCorr_carpetCH0, AutoCorr_carpetCH1, CrossCorr_carpet01,kcountCH0,kcountCH1,numberNandBCH0,numberNandBCH1,brightnessNandBCH0,brightnessNandBCH1,CV,signal_to_noiseCH0,signal_to_noiseCH1
        

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
            self.numOfCH = 1
            temp = np.array(self.imDataStore).astype(np.float64)
            
            if temp.shape.__len__() == 2 or  (temp.shape.__len__() ==3 and temp.shape[0] < 3 and temp.shape[0]==1):
                self.CH0 = temp.reshape(temp.shape[0],temp.shape[1])
            elif temp.shape.__len__() ==3 and temp.shape[0] > 2:
                self.CH0 = temp.reshape(temp.shape[0]*temp.shape[1],temp.shape[2])
            elif  (temp.shape.__len__() ==3 and temp.shape[0] < 3 and temp.shape[0]==2):
                self.CH0 = copy.deepcopy(temp[0,:,:])
                self.CH1 = copy.deepcopy(temp[1,:,:])
                self.numOfCH = 2
                if self.end_pt != 0:
                    self.CH0 = np.array(self.CH0[self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
                    self.CH1 = np.array(self.CH1[self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
                if np.sum(self.CH1) ==0:
                    self.numOfCH =1
            elif temp.shape.__len__() ==4:
                self.CH0 = copy.deepcopy(temp[:,0,:,:])
                self.CH1 = copy.deepcopy(temp[:,0,:,:])
                self.CH0 = self.CH0.reshape(self.CH0.shape[0]*self.CH0.shape[1],self.CH0.shape[2])
                self.CH1 = self.CH1.reshape(self.CH1.shape[0]*self.CH1.shape[1],self.CH1.shape[2])
                if np.sum(self.CH1) ==0:
                    self.numOfCH =1
            
            if self.cmin == None:
                self.cmin = 0
            if self.cmax == None:
                self.cmax = self.CH0.shape[1]
            
            
            
            if self.end_pt != 0 and self.numOfCH == 1:
                self.CH0 = np.array(self.CH0[self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
                
            if self.end_pt != 0 and self.numOfCH == 2:
                self.CH0 = np.array(self.CH0[self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
                self.CH1 = np.array(self.CH1[self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
            

            self.CH0_pc = np.zeros((self.CH0.shape))
            if self.numOfCH == 2:
                self.CH1_pc = np.zeros((self.CH1.shape))

            
        
        elif self.ext == 'lsm':
            
            #For lsm files the dimensions can vary.
            if self.imDataStore.shape.__len__() > 2:
                self.dimSize = [self.imDataStore.shape[1],self.imDataStore.shape[2]]
                self.numOfCH = 2
            else:
                self.dimSize = [self.imDataStore.shape[0],self.imDataStore.shape[1]]
                self.numOfCH = 1
            
            if self.numOfCH == 2:
                if np.sum(self.imDataStore[0,:,:]) == 0:
                    self.imDataStore[:,:] = self.imDataStore[1,:,:]
                    self.numOfCH = 1
                if np.sum(self.imDataStore[1,:,:]) == 0:
                    self.imDataStore[:,:] = self.imDataStore[0,:,:]
                    self.numOfCH = 1



            self.name = str(self.filepath).split('/')[-1]
            self.deltat = self.imDataDesc[0]
            self.dwell_time = self.imDataDesc[1]
            if self.cmin == None:
                self.cmin = 0
            if self.cmax == None:
                self.cmax = self.dimSize[0]
            
            
            if self.imDataStore.shape.__len__() > 2:
                self.CH0 = np.array(self.imDataStore[0,:,:]).astype(np.float64)
                if self.end_pt != 0:
                    self.CH0 = np.array(self.imDataStore[0,self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
            else:
                self.CH0 = np.array(self.imDataStore[:,:]).astype(np.float64)
                if self.end_pt != 0:
                    self.CH0 = np.array(self.imDataStore[self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
            self.CH0_pc = np.zeros((self.CH0.shape))

           
            
            if self.numOfCH ==2:
                self.CH1 = np.array(self.imDataStore[1,:,:]).astype(np.float64)
                if self.end_pt != 0:
                    self.CH1 = np.array(self.imDataStore[1,self.start_pt:self.end_pt,self.cmin:self.cmax]).astype(np.float64)
                self.CH1_pc = np.zeros((self.CH1.shape))

        elif self.ext == 'msr':
    
            self.name = self.imDataDesc[7]
            self.dwell_time = float(self.imDataDesc[6])
            
            #self.memSize = int(self.imDataDesc[1])
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
                    
                    self.CH0 = np.array(self.imDataStore.T)
                    if self.cmin == None:
                        self.cmin = 0
                    if self.cmax == None:
                        self.cmax = self.CH0.shape[1]
                    
                    #This is for the crop function
                    if self.end_pt != 0:
                        self.CH0 = self.CH0[self.start_pt:self.end_pt,self.cmin:self.cmax]
                    self.CH0_pc = np.zeros((self.CH0.shape))
        
        elif self.ext == 'lif' :
    
            self.name = self.imDataDesc['name']
            self.dwell_time = float(self.imDataDesc['dwelltime'])
            
            #self.memSize = int(self.imDataDesc[1])
            self.LUTName = self.imDataDesc['lutname']
            self.dimSize = [int(self.imDataDesc['diminfo'][0]),int(self.imDataDesc['diminfo'][1]),int(self.imDataDesc['diminfo'][2])]
            #For display we divide image into sections or panes.
            
            #Convert to ms, default is seconds.
            self.deltat  = float(self.imDataDesc['linetime'][0])*1000
            
            tempList0 =[];
            tempList1 =[];

            self.numOfCH = self.LUTName.__len__();
            

            if self.cmin == None:
                self.cmin = 0
            if self.cmax == None:
                self.cmax = self.dimSize[0]



            #Single channel is simple to reshape from pages.
            if self.numOfCH == 1:
                    
                    self.CH0 = np.array(self.imDataStore).reshape(self.dimSize[1]*self.dimSize[2],self.dimSize[0])


                    #This is for the crop function
                    if self.end_pt != 0:
                        self.CH0 = self.CH0[self.start_pt:self.end_pt,self.cmin:self.cmax]
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
                        self.CH0 = self.CH0[self.start_pt:self.end_pt,self.cmin:self.cmax]
                    
                    self.CH1 = np.array(tempList1).reshape(self.dimSize[1]*self.dimSize[2],self.dimSize[0])
                    #This is for the crop function.
                    if self.end_pt != 0:
                        self.CH1 = self.CH1[self.start_pt:self.end_pt,self.cmin:self.cmax]
                    
                    self.CH0_pc = np.zeros((self.CH0.shape))
                    self.CH1_pc = np.zeros((self.CH1.shape))
                    
            

            
            self.deltat = float(self.deltat);

        #calculated to establish how many panes the time-series has.
        self.maxPane= np.floor(float(self.dimSize[1])/((float(self.CH0.shape[1]))/64)*150)
        
        self.CH0_arraySum = np.sum(self.CH0[:,:],1).astype(np.float64)
        self.CH0_arrayColSum = np.sum(self.CH0[:,:],0).astype(np.float64)

        
        if np.sum(self.CH0_arraySum) == 0:
            print('intensity trace excluded as contained no intensity signal:', self.file_name)
            self.parObj.objectRef.pop(self.parObj.numOfLoaded)
            self.parObj.numOfLoaded = self.parObj.numOfLoaded - 1
            return
            

        
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


        #Find the length of the generated correlation function.
        
        k = int(np.floor(np.log2(self.num_of_lines/self.m)))
        self.lenG = np.int(np.floor(self.m + k*self.m/2))
        mar = int((self.spatialBin-1)/2)


        AC_all_CH0 = np.zeros((np.int(np.floor(self.m + k*self.m/2)),int(self.CH0.shape[1]-(2*mar)),int(1+np.ceil(self.CH0.shape[0]-self.num_of_lines)/self.num_of_lines)))
        if self.numOfCH==2:
            AC_all_CH1  = np.zeros((AC_all_CH0.shape))
            CC_all_CH01 = np.zeros((AC_all_CH0.shape))
        
        c = 0
        for stx in range(start_x,self.CH0.shape[0]-self.num_of_lines+1,self.num_of_lines):
            #Function which calculates the correlation carpet.
            if self.numOfCH==1:
                self.corrArrScale, AC_carCH0, ap, aq, self.kcountCH0,cq,self.numberNandBCH0,dq,self.brightnessNandBCH0,vq,cq,self.s2nCH0, dq = self.calc_carpet(self.CH0[stx:stx+self.num_of_lines,:],None,self.lenG)
                AC_all_CH0[:,:,c] = AC_carCH0


            elif self.numOfCH==2:
                self.corrArrScale, AC_carCH0, AC_carCH1, CC_carCH01,self.kcountCH0,self.kcountCH1,self.numberNandBCH0,self.numberNandBCH1,self.brightnessNandBCH0,self.brightnessNandBCH1,self.CV, self.s2nCH0,self.s2nCH1 = self.calc_carpet(self.CH0[stx:stx+self.num_of_lines,:],self.CH1[stx:stx+self.num_of_lines,:],self.lenG)
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
    #Signal to noise
    def calc_signal_to_noise(self,int_ch,AC):
        a = np.copy(int_ch)
        size = int(a.size)
        hf_sz = size//2
        # subtract mean and pad with zeros to twice the size
        a_mean = a.mean().astype(np.float64)
        #Has the padding in
        a = np.pad(a-a_mean, a.size//2, mode='constant')
        M = np.int32((AC[:,0])*self.deltat/1000.0)
        c = np.zeros((AC.shape[0])).astype(np.float64)
        ct = 0
        for tau in M:
            c[ct] = np.var(a[hf_sz:-hf_sz]*a[tau:size+tau])
            ct += 1
        varG = (1.0/(size*a_mean**4))*c


        s2n = np.average(np.abs(AC[:,1]/varG**0.5))
        return s2n


    
        



