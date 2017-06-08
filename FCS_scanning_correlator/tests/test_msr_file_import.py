from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np

def test_msr_file_import(par_obj,win_obj):
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
		#assert win_obj.diag.dialog_dwell_win.isVisible() == False

	##Test MSR file import.
	win_obj.test_path = []
	win_obj.test_path.append(os.getcwd()+'/test_files/3 (505 Hz).msr')
	win_obj.test_path.append(os.getcwd()+'/test_files/2 (245Hz).msr')
	win_obj.test_path.append(os.getcwd()+'/test_files/1.msr')
	
	
	
	
	for i in range(0, win_obj.test_path.__len__()):
		win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path)


	assert win_obj.diag.main_dialog_win.check1.isVisible() == True
	assert win_obj.diag.main_dialog_win.check2.isVisible() == True
	assert win_obj.diag.main_dialog_win.check3.isVisible() == True
	assert win_obj.diag.main_dialog_win.check4.isVisible() == True
	assert win_obj.diag.main_dialog_win.check5.isVisible() == True

	win_obj.diag.main_dialog_win.check1.click()
	win_obj.diag.main_dialog_win.check2.click()
	
	win_obj.diag.main_dialog_win.check4.click()
	win_obj.diag.main_dialog_win.check5.click()
	QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
	assert win_obj.diag.isVisible() == False
	
	#Goes through first file.
	for i in range(0,4):
		#Open the dialog for the line sampling (Hz):
		test_line_sampling_dialog(505 + (i*4))
		#Open the dialog for inputing the dwell time.
		test_dwell_dialog(2.15 + (i*0.01))
		#Open the dialog for asking whether to continue asking for details or not.
		if i < 3:
			assert win_obj.diag.use_settings_win.isVisible() == True
			QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)
			assert win_obj.diag.use_settings_win.isVisible() == False

	assert win_obj.diag.main_dialog_win.check2.isVisible() == True
	

	#Open second file.
	win_obj.diag.main_dialog_win.check2.click()
	QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
	assert win_obj.diag.isVisible() == False
	test_line_sampling_dialog(505)
	#Open the dialog for inputing the dwell time.
	test_dwell_dialog(2.15)
	assert win_obj.diag.use_settings_win.isVisible() == True
	QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)
	



	#Open third file.
	assert win_obj.diag.main_dialog_win.check2.isVisible() == True
	win_obj.diag.main_dialog_win.check2.click()
	QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
	assert win_obj.diag.isVisible() == False
	test_line_sampling_dialog(505)
	#Open the dialog for inputing the dwell time.
	test_dwell_dialog(2.15)
	assert win_obj.diag.use_settings_win.isVisible() == True
	QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)
	assert win_obj.diag.use_settings_win.isVisible() == False


	#Check that the line sampling dialog doesn't appear again.
	assert win_obj.diag.line_sampling_win.isVisible() == False
	#Check the files are properly named.
	assert par_obj.objectRef[0].name == 'ExpControl #0 {0}'
	assert par_obj.objectRef[0].name == 'ExpControl #0 {0}'
	assert par_obj.objectRef[1].name == 'ExpControl #0 {1}'
	assert par_obj.objectRef[2].name == 'ExpControl #0 {3}'
	assert par_obj.objectRef[3].name == 'ExpControl #0 {4}'
	assert par_obj.objectRef[4].name == 'ExpControl #1 {3}'
	assert par_obj.objectRef[5].name == 'ExpControl #1 {98}'

	assert par_obj.objectRef[0].CH0.shape == (8192,50)
	assert par_obj.objectRef[1].CH0.shape == (5000,50)
	assert par_obj.objectRef[2].CH0.shape == (5000,50)
	assert par_obj.objectRef[3].CH0.shape == (5050,50)
	assert par_obj.objectRef[4].CH0.shape == (2450,125)
	assert par_obj.objectRef[5].CH0.shape == (4465,40)
	assert par_obj.objectRef[0].CH0_pc.shape == (8192,50)
	assert par_obj.objectRef[1].CH0_pc.shape == (5000,50)
	assert par_obj.objectRef[2].CH0_pc.shape == (5000,50)
	assert par_obj.objectRef[3].CH0_pc.shape == (5050,50)
	assert par_obj.objectRef[4].CH0_pc.shape == (2450,125)
	assert par_obj.objectRef[5].CH0_pc.shape == (4465,40)

	assert par_obj.objectRef[0].deltat == 1000.0/float(505)
	assert par_obj.objectRef[0].dwell_time == float(2.15)/1000000.0
	
	#Tests that the settings are propagated to the scanning software file structure correctly
	assert np.round(par_obj.objectRef[1].deltat,5) == np.round(1000.0/float(505+ (1*4)),5)
	assert np.round(par_obj.objectRef[1].dwell_time,5) == np.round(((2.15+ (1*0.01))/1000000.0),5)
	assert np.round(par_obj.objectRef[2].deltat,5) == np.round(1000.0/float(505+ (2*4)),5)
	assert np.round(par_obj.objectRef[2].dwell_time,5) == np.round(((2.15+ (2*0.01))/1000000.0),5)
	assert np.round(par_obj.objectRef[3].deltat,5) == np.round(1000.0/float(505+ (3*4)),5)
	assert np.round(par_obj.objectRef[3].dwell_time,5) == np.round(((2.15 + (3*0.01))/1000000.0),5)
	assert par_obj.objectRef[4].deltat == 1000.0/float(505)
	assert par_obj.objectRef[4].dwell_time == float(2.15)/1000000.0
	assert par_obj.objectRef[5].deltat == 1000.0/float(505)
	assert par_obj.objectRef[5].dwell_time == float(2.15)/1000000.0


	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 6
	for i in range(5,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0

	

	for i in range(0, win_obj.test_path.__len__()):
		win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path)

	
	assert win_obj.diag.main_dialog_win.check1.isVisible() == True
	assert win_obj.diag.main_dialog_win.check2.isVisible() == True
	assert win_obj.diag.main_dialog_win.check3.isVisible() == True
	assert win_obj.diag.main_dialog_win.check4.isVisible() == True
	assert win_obj.diag.main_dialog_win.check5.isVisible() == True
	win_obj.diag.main_dialog_win.check1.click()
	win_obj.diag.main_dialog_win.check2.click()
	
	win_obj.diag.main_dialog_win.check4.click()
	win_obj.diag.main_dialog_win.check5.click()
	
	QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
	assert win_obj.diag.isVisible() == False
	

	#Opens file and then applies same settings to all.
	#Open the dialog for the line sampling (Hz):
	test_line_sampling_dialog(505 )
	#Open the dialog for inputing the dwell time.
	test_dwell_dialog(2.15 )
	#Open the dialog for asking whether to continue asking for details or not.
	assert win_obj.diag.use_settings_win.isVisible() == True
	QTest.mouseClick(win_obj.diag.yes, QtCore.Qt.LeftButton)
	
	
	assert win_obj.diag.main_dialog_win.check2.isVisible() == True
	
	#Load second file.
	win_obj.diag.main_dialog_win.check2.click()
	QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
	
	#Load third file.
	win_obj.diag.main_dialog_win.check2.click()
	QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)


	#Checks the values of the imported data. 
	for i in range(0,6):
		assert par_obj.objectRef[i].deltat == 1000.0/float(505)
		assert par_obj.objectRef[i].dwell_time == float(2.15)/1000000.0

	#Check the files are properly named.
	assert par_obj.objectRef[0].name == 'ExpControl #0 {0}'
	assert par_obj.objectRef[1].name == 'ExpControl #0 {1}'
	assert par_obj.objectRef[2].name == 'ExpControl #0 {3}'
	assert par_obj.objectRef[3].name == 'ExpControl #0 {4}'
	assert par_obj.objectRef[4].name == 'ExpControl #1 {3}'
	assert par_obj.objectRef[5].name == 'ExpControl #1 {98}'

	#Check dimensions.
	assert par_obj.objectRef[0].CH0.shape == (8192,50)
	assert par_obj.objectRef[1].CH0.shape == (5000,50)
	assert par_obj.objectRef[2].CH0.shape == (5000,50)
	assert par_obj.objectRef[3].CH0.shape == (5050,50)
	assert par_obj.objectRef[4].CH0.shape == (2450,125)
	assert par_obj.objectRef[5].CH0.shape == (4465,40)
	
	
	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 6
	for i in range(5,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0	
	

	print 'tests finished. MSR Import looks fine'
	return True