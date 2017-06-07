from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np

def test_lif_file_import(par_obj,win_obj):
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
		#assert win_obj.diag.dialog_dwell_win.isVisible() == False

	##Test MSR file import.
	win_obj.test_path = []
	win_obj.test_path.append(os.getcwd()+'/test_files/Jurkat-SNAP-actin_scanningFCS.lif')
	win_obj.test_path.append(os.getcwd()+'/test_files/20150409_JCamSTED HG LCK-Cit_LCK-SiR.lif')
	
	
	
	
	
	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	btns = win_obj.file_import.file_dialog.findChildren(QtGui.QPushButton)
	
	#This was very painful to come up with. This and next paragraph won't work if shortened into a for loop. I have no idea why.
	win_obj.file_import.file_dialog.selectFile(win_obj.test_path[0])
	select_0 = win_obj.file_import.file_dialog.tree.selectionModel().selectedIndexes()
	win_obj.file_import.file_dialog.selectFile(win_obj.test_path[1])
	select_1 = win_obj.file_import.file_dialog.tree.selectionModel().selectedIndexes()
	
	#The Qrage parameter expresses my anger at the time.
	Qrage = QtGui.QItemSelection(select_0[0],select_0[0])
	win_obj.file_import.file_dialog.tree.selectionModel().select(Qrage,QtGui.QItemSelectionModel.Select)
	Qrage = QtGui.QItemSelection(select_1[0],select_1[0])
	win_obj.file_import.file_dialog.tree.selectionModel().select(Qrage,QtGui.QItemSelectionModel.Select)
	
	


	
	QTest.mouseClick(btns[0], QtCore.Qt.LeftButton)

	for i in range(0,14):
		print i
		assert win_obj.diag.lif_import_win.item_list[i].checkState() == False
	

	win_obj.diag.lif_import_win.item_list[0].setCheckState(QtCore.Qt.Checked)
	win_obj.diag.lif_import_win.item_list[4].setCheckState(QtCore.Qt.Checked)
	win_obj.diag.lif_import_win.item_list[6].setCheckState(QtCore.Qt.Checked)
	win_obj.diag.lif_import_win.item_list[9].setCheckState(QtCore.Qt.Checked)

	#These files are empty as so will make the system fail.
	QTest.mouseClick(win_obj.diag.load_data_btn, QtCore.Qt.LeftButton)
	win_obj.diag.lif_import_win.item_list[0].setCheckState(QtCore.Qt.Checked)
	win_obj.diag.lif_import_win.item_list[4].setCheckState(QtCore.Qt.Checked)
	win_obj.diag.lif_import_win.item_list[6].setCheckState(QtCore.Qt.Checked)
	win_obj.diag.lif_import_win.item_list[9].setCheckState(QtCore.Qt.Checked)
	QTest.mouseClick(win_obj.diag.load_data_btn, QtCore.Qt.LeftButton)

	print 'shape',par_obj.objectRef[0].CH0.shape
	assert par_obj.objectRef[0].CH0.shape == (24576, 64)
	assert par_obj.objectRef[1].CH0.shape == (24576, 64)
	assert par_obj.objectRef[2].CH0.shape == (24576, 64)
	assert par_obj.objectRef[3].CH0.shape == (106496, 64)
	assert par_obj.objectRef[0].CH0_pc.shape == (24576, 64)
	assert par_obj.objectRef[1].CH0_pc.shape == (24576, 64)
	assert par_obj.objectRef[2].CH0_pc.shape == (24576, 64)
	assert par_obj.objectRef[3].CH0_pc.shape == (106496, 64)


	assert par_obj.objectRef[0].name == '1_Jurkat-SNAP-Actin_TMR_e552_0STED_24576f_1800Hz_z4864px'
	assert par_obj.objectRef[1].name == '3_Jurkat-SNAP-Actin_TMR_e552_0STED_24576f_1800Hz_z4864px_12bit'
	assert par_obj.objectRef[2].name == '4_Jurkat-SNAP-Actin_TMR_e552_0STED_24576f_1800Hz_z4864px_12bit'
	assert par_obj.objectRef[3].name == '5_Jurkat-SNAP-Actin_TMR_e552_00STED_106496f_8000Hz_z48_64px_12bit'
	

	assert np.round(np.average(par_obj.objectRef[3].CH0),3) == 1140.479
	assert np.round(np.min(par_obj.objectRef[3].CH0),3) == 0.000
	assert np.round(np.max(par_obj.objectRef[3].CH0),3) == 4095.000
	assert np.round(np.median(par_obj.objectRef[3].CH0),3) == 1097

	print np.round(np.average(par_obj.objectRef[3].CH0[:,0]),3) == 1133.802
	print np.round(np.min(par_obj.objectRef[3].CH0[:,0]),3) == 0.000
	print np.round(np.max(par_obj.objectRef[3].CH0[:,0]),3) == 3568
	print np.round(np.median(par_obj.objectRef[3].CH0[:,0]),3) == 1086

	#Tests how many files appear in main interface and then closes them.
	assert par_obj.numOfLoaded == 4
	for i in range(3,-1,-1):
		QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
	assert par_obj.numOfLoaded == 0
	

	print 'tests finished. LIF Import looks fine'
	return True