from PyQt5.QtTest import QTest
from PyQt5 import QtGui, QtCore
import os
import numpy as np

def test_lsm_file_import(par_obj,win_obj):
	def test_line_sampling_dialog(sample_rate):
		#Open the dialog for the line sampling (Hz):
		assert win_obj.diag.line_sampling_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		assert str(win_obj.diag.label.text()) == 'Enter the line sampling (Hz):'
		win_obj.diag.input_text.clear()
		QTest.keyClicks(win_obj.diag.input_text, str(sample_rate))
		assert win_obj.diag.input_text.text() == str(sample_rate)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.line_sampling_win.isVisible() == False
	
	def test_dwell_dialog(dwell_time):
		#Open the dialog for inputing the dwell time.
		assert win_obj.diag.dialog_dwell_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		win_obj.diag.input_text.clear()
		assert str(win_obj.diag.label.text()) == 'Enter the pixel dwell time (us):'
		QTest.keyClicks(win_obj.diag.input_text, str(dwell_time))
		assert win_obj.diag.input_text.text() == str(dwell_time)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.dialog_dwell_win.isVisible() == False

	##Test MSR file import.
	win_obj.test_path = []
	win_obj.test_path.append(os.getcwd()+'/test_files/2.lsm')
	win_obj.test_path.append(os.getcwd()+'/test_files/Perp Scanning 0degree.lsm')
	win_obj.test_path.append(os.getcwd()+'/test_files/Perp Scanning 90degree.lsm')
	
	for i in range(0, win_obj.test_path.__len__()):
		win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path)
	
	#assert win_obj.diag.line_sampling_win.isVisible() == True
	
	

	#Goes through first file.
	for i in range(0,3):
		#Open the dialog for the line sampling (Hz):
		print  (win_obj.diag.input_text.text())
		test_line_sampling_dialog(str(float(win_obj.diag.input_text.text())+ (i*4.)))
		#Open the dialog for inputing the dwell time.
		test_dwell_dialog(2.15 + (i*0.01))
		#Open the dialog for asking whether to continue asking for details or not.
		print (i)
		
		if i < 2:
			assert win_obj.diag.use_settings_win.isVisible() == True
			QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)
			#assert win_obj.diag.use_settings_win.isVisible() == False
	
	#Check that the line sampling dialog doesn't appear again.
	assert win_obj.diag.line_sampling_win.isVisible() == False
	
	#Check the files are properly named.
	assert par_obj.objectRef[0].name == '2.lsm'
	assert par_obj.objectRef[1].name == 'Perp Scanning 0degree.lsm'
	assert par_obj.objectRef[2].name == 'Perp Scanning 90degree.lsm'
	

	assert par_obj.objectRef[0].CH0.shape == (50000,512)
	assert par_obj.objectRef[0].CH1.shape == (50000,512)
	assert par_obj.objectRef[1].CH0.shape == (50000,512)
	assert par_obj.objectRef[2].CH0.shape == (50000,512)
	assert par_obj.objectRef[0].CH0_pc.shape == (50000,512)
	assert par_obj.objectRef[0].CH1_pc.shape == (50000,512)
	assert par_obj.objectRef[1].CH0_pc.shape == (50000,512)
	assert par_obj.objectRef[2].CH0_pc.shape == (50000,512)
	

	assert np.round(par_obj.objectRef[0].deltat,5) == np.round(1000.0/float(2115.38461538),5)
	assert par_obj.objectRef[0].dwell_time == float(2.15)/1000000.0
	
	#Tests that the settings are propagated to the scanning software file structure correctly
	assert np.round(par_obj.objectRef[1].deltat,5) == np.round(1000.0/float(2115.38461538+ (1*4.)),5)
	assert np.round(par_obj.objectRef[1].dwell_time,5) == np.round(((2.15+ (1*0.01))/1000000.0),5)
	assert np.round(par_obj.objectRef[2].deltat,5) == np.round(1000.0/float(2115.38461538+ (2*4.)),5)
	assert np.round(par_obj.objectRef[2].dwell_time,5) == np.round(((2.15+ (2*0.01))/1000000.0),5)
	

	
	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 3
	for i in range(2,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0

	for i in range(0, win_obj.test_path.__len__()):
		win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path)

	#Open the dialog for the line sampling (Hz):
	test_line_sampling_dialog(1800 )
	#Open the dialog for inputing the dwell time.
	test_dwell_dialog(2.15 )
	#Open the dialog for asking whether to continue asking for details or not.
	assert win_obj.diag.use_settings_win.isVisible() == True
	QTest.mouseClick(win_obj.diag.yes, QtCore.Qt.LeftButton)
	

	#Checks the values of the imported data. 
	for i in range(0,3):
		assert par_obj.objectRef[i].deltat == 1000.0/float(1800)
		assert par_obj.objectRef[i].dwell_time == float(2.15)/1000000.0

	#Check the files are properly named.
	assert par_obj.objectRef[0].name == '2.lsm'
	assert par_obj.objectRef[1].name == 'Perp Scanning 0degree.lsm'
	assert par_obj.objectRef[2].name == 'Perp Scanning 90degree.lsm'

	assert par_obj.objectRef[0].CH0.shape == (50000,512)
	assert par_obj.objectRef[0].CH1.shape == (50000,512)
	assert par_obj.objectRef[1].CH0.shape == (50000,512)
	assert par_obj.objectRef[2].CH0.shape == (50000,512)

	#Check the bit-depth is correct.
	assert par_obj.objectRef[0].CH0.dtype == np.float64
	assert par_obj.objectRef[0].CH1.dtype == np.float64
	assert par_obj.objectRef[1].CH0.dtype == np.float64
	assert par_obj.objectRef[2].CH0.dtype == np.float64
	


	#Compare the intensity values to those we have measured in ImageJ/Fiji
	assert np.round(np.average(par_obj.objectRef[0].CH0[:,0]),3) == 4.540
	assert np.round(np.min(par_obj.objectRef[0].CH0[:,0]),3) == 0.000
	assert np.round(np.max(par_obj.objectRef[0].CH0[:,0]),3) == 96.000
	assert np.round(np.median(par_obj.objectRef[0].CH0[:,0]),3) == 2.000
	assert np.round(np.average(par_obj.objectRef[0].CH1[:,0]),3) == 1.808
	assert np.round(np.min(par_obj.objectRef[0].CH1[:,0]),3) == 0.000
	assert np.round(np.max(par_obj.objectRef[0].CH1[:,0]),3) == 130.000
	assert np.round(np.median(par_obj.objectRef[0].CH1[:,0]),3) == 0.000
	assert np.round(np.average(par_obj.objectRef[0].CH0[:,:]),3) == 4.509
	assert np.round(np.min(par_obj.objectRef[0].CH0[:,:]),3) == 0.000
	assert np.round(np.max(par_obj.objectRef[0].CH0[:,:]),3) == 217.000
	assert np.round(np.median(par_obj.objectRef[0].CH0[:,:]),3) == 2.000
	
	
	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 3
	for i in range(2,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0
	
	

	print ('tests finished. lsm Import looks fine')
	return True