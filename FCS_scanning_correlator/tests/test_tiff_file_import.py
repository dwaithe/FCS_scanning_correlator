from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np

def test_tiff_file_import(par_obj,win_obj):
	def test_line_sampling_dialog(sample_rate):
		#Open the dialog for the line sampling (Hz):
		assert win_obj.diag.line_sampling_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		assert str(win_obj.diag.label.text()) == 'Enter the line sampling (Hz):'
		QTest.keyClicks(win_obj.diag.input_text, str(sample_rate))
		assert win_obj.diag.input_text.text() == str(sample_rate)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.line_sampling_win.isVisible() == False
	
	def test_dwell_dialog(dwell_time):
		#Open the dialog for inputing the dwell time.
		assert win_obj.diag.dialog_dwell_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		assert str(win_obj.diag.label.text()) == 'Enter the pixel dwell time (us):'
		QTest.keyClicks(win_obj.diag.input_text, str(dwell_time))
		assert win_obj.diag.input_text.text() == str(dwell_time)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.dialog_dwell_win.isVisible() == False

	##Test MSR file import.
	win_obj.test_path = []
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_4_.tif')
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_5_.tif')
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_6_.tif')
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_7_.tif')
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_.tif')
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_shift.tif')
	win_obj.test_path.append(os.getcwd()+'/test_files/out_img_D_0p2_noi_yes_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_shift-1.tif with additive Gaussian noise.tif')
	
	for i in range(0, win_obj.test_path.__len__()):
		win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path[0:4])

	assert win_obj.diag.line_sampling_win.isVisible() == True

	
	
	#Goes through first file.
	for i in range(0,4):
		#Open the dialog for the line sampling (Hz):
		test_line_sampling_dialog(1800 + (i*4))
		#Open the dialog for inputing the dwell time.
		test_dwell_dialog(2.15 + (i*0.01))
		#Open the dialog for asking whether to continue asking for details or not.
		print i
		if i < 3:
			assert win_obj.diag.use_settings_win.isVisible() == True
			QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)

			#assert win_obj.diag.use_settings_win.isVisible() == False
	
	#Check that the line sampling dialog doesn't appear again.
	assert win_obj.diag.line_sampling_win.isVisible() == False

	#Check the files are properly named.
	assert par_obj.objectRef[0].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_4_.tif'
	assert par_obj.objectRef[1].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_5_.tif'
	assert par_obj.objectRef[2].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_6_.tif'
	assert par_obj.objectRef[3].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_7_.tif'

	assert par_obj.objectRef[0].CH0.shape == (54000,64)
	assert par_obj.objectRef[1].CH0.shape == (54000,64)
	assert par_obj.objectRef[2].CH0.shape == (54000,64)
	assert par_obj.objectRef[3].CH0.shape == (54000,64)

	assert par_obj.objectRef[0].deltat == 1000.0/float(1800)
	assert par_obj.objectRef[0].dwell_time == float(2.15)/1000000.0
	
	#Tests that the settings are propagated to the scanning software file structure correctly
	assert np.round(par_obj.objectRef[1].deltat,5) == np.round(1000.0/float(1800+ (1*4)),5)
	assert np.round(par_obj.objectRef[1].dwell_time,5) == np.round(((2.15+ (1*0.01))/1000000.0),5)
	assert np.round(par_obj.objectRef[2].deltat,5) == np.round(1000.0/float(1800+ (2*4)),5)
	assert np.round(par_obj.objectRef[2].dwell_time,5) == np.round(((2.15+ (2*0.01))/1000000.0),5)
	assert np.round(par_obj.objectRef[3].deltat,5) == np.round(1000.0/float(1800+ (3*4)),5)
	assert np.round(par_obj.objectRef[3].dwell_time,5) == np.round(((2.15 + (3*0.01))/1000000.0),5)

	#Test carpet values.
	assert np.round(np.average(par_obj.objectRef[0].CH0[:,0]),3) == 0.569
	assert np.round(np.min(par_obj.objectRef[0].CH0[:,0]),3) == 0.000
	assert np.round(np.max(par_obj.objectRef[0].CH0[:,0]),3) == 3.836
	assert np.round(np.median(par_obj.objectRef[0].CH0[:,0]),3) == 0.441


	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 4
	for i in range(3,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0

	#Opens file and then applies same settings to all.
	

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path[0:4])
	#Open the dialog for the line sampling (Hz):
	test_line_sampling_dialog(1800 )
	#Open the dialog for inputing the dwell time.
	test_dwell_dialog(2.15 )
	#Open the dialog for asking whether to continue asking for details or not.
	assert win_obj.diag.use_settings_win.isVisible() == True
	QTest.mouseClick(win_obj.diag.yes, QtCore.Qt.LeftButton)
	

	#Checks the values of the imported data. 
	for i in range(0,4):
		assert par_obj.objectRef[i].deltat == 1000.0/float(1800)
		assert par_obj.objectRef[i].dwell_time == float(2.15)/1000000.0

	#Check the files are properly named.
	assert par_obj.objectRef[0].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_4_.tif'
	assert par_obj.objectRef[1].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_5_.tif'
	assert par_obj.objectRef[2].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_6_.tif'
	assert par_obj.objectRef[3].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_7_.tif'

	assert par_obj.objectRef[0].CH0.shape == (54000,64)
	assert par_obj.objectRef[1].CH0.shape == (54000,64)
	assert par_obj.objectRef[2].CH0.shape == (54000,64)
	assert par_obj.objectRef[3].CH0.shape == (54000,64)

	#Check the bit-depth is correct.
	assert par_obj.objectRef[0].CH0.dtype == np.float64
	assert par_obj.objectRef[1].CH0.dtype == np.float64
	assert par_obj.objectRef[2].CH0.dtype == np.float64
	assert par_obj.objectRef[3].CH0.dtype == np.float64

	#Test carpet values.
	assert np.round(np.average(par_obj.objectRef[0].CH0[:,0]),3) == 0.569
	assert np.round(np.min(par_obj.objectRef[0].CH0[:,0]),3) == 0.000
	assert np.round(np.max(par_obj.objectRef[0].CH0[:,0]),3) == 3.836
	assert np.round(np.median(par_obj.objectRef[0].CH0[:,0]),3) == 0.441
	
	
	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 4
	for i in range(3,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0

	#multi channel tiff import.

		#Opens file and then applies same settings to all.
	

	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.file_import.file_dialog.done(1,win_obj.test_path[4:7])
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
	assert par_obj.objectRef[0].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_.tif'
	assert par_obj.objectRef[1].name == 'out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_shift.tif'
	assert par_obj.objectRef[2].name == 'out_img_D_0p2_noi_yes_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_shift-1.tif with additive Gaussian noise.tif'

	assert par_obj.objectRef[0].CH0_pc.shape == (54000,64)
	assert par_obj.objectRef[1].CH0_pc.shape == (54000,64)
	assert par_obj.objectRef[2].CH0_pc.shape == (54000,64)
	assert par_obj.objectRef[0].CH1_pc.shape == (54000,64)
	assert par_obj.objectRef[1].CH1_pc.shape == (54000,64)
	assert par_obj.objectRef[2].CH1_pc.shape == (54000,64)
	assert par_obj.objectRef[0].CH0_pc.shape == (54000,64)
	assert par_obj.objectRef[1].CH0_pc.shape == (54000,64)
	assert par_obj.objectRef[2].CH0_pc.shape == (54000,64)
	assert par_obj.objectRef[0].CH1_pc.shape == (54000,64)
	assert par_obj.objectRef[1].CH1_pc.shape == (54000,64)
	assert par_obj.objectRef[2].CH1_pc.shape == (54000,64)


	#Check the bit-depth is correct.
	assert par_obj.objectRef[0].CH0.dtype == np.float64
	assert par_obj.objectRef[1].CH0.dtype == np.float64
	assert par_obj.objectRef[2].CH0.dtype == np.float64
	assert par_obj.objectRef[0].CH1.dtype == np.float64
	assert par_obj.objectRef[1].CH1.dtype == np.float64
	assert par_obj.objectRef[2].CH1.dtype == np.float64
	

	#Test carpet values.
	#assert np.round(np.average(par_obj.objectRef[0].CH0[:,0]),3) == 0.569
	#assert np.round(np.min(par_obj.objectRef[0].CH0[:,0]),3) == 0.000
	#assert np.round(np.max(par_obj.objectRef[0].CH0[:,0]),3) == 3.836
	#assert np.round(np.median(par_obj.objectRef[0].CH0[:,0]),3) == 0.441
	
	
	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 3
	for i in range(2,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0
	


	print 'tests finished. TIFF Import looks fine'
	return True