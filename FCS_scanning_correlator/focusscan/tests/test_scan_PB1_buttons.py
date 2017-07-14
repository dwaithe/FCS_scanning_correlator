from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np

def test_scan_PB1_buttons(par_obj,win_obj):
	
		
		QTest.mouseClick(win_obj.prev_pane, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.next_pane, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.crop_data_btn, QtCore.Qt.LeftButton) 
		QTest.mouseClick(win_obj.reprocess_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.bleach_corr1_btn, QtCore.Qt.LeftButton) 
		QTest.mouseClick(win_obj.bleach_corr_on_off, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.bleach_corr2_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.CH0Auto_btn , QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.CH1Auto_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.CH01Cross_btn, QtCore.Qt.LeftButton) 
		QTest.mouseClick(win_obj.addRegion_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.clear_region_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.save_corr_carpet_btn, QtCore.Qt.LeftButton) 
		#QTest.mouseClick(win_obj.save_log_corr_carpet_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.export_all_data_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.export_region_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.export_all_data_to_csv_btn, QtCore.Qt.LeftButton)
		
		
		win_obj.test_path = [os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_with_PBC.tif']
		win_obj.test_path[0] = win_obj.test_path[0].replace('\\','/')

		QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
		win_obj.file_import.file_dialog.done(1,win_obj.test_path)

		#Open the dialog for the line sampling (Hz):
		assert win_obj.diag.line_sampling_win.isVisible() == True, "Dialog for line sampling did not open."
		assert win_obj.diag.input_text.isVisible() == True, "Text input for line sampling did not open."
		assert str(win_obj.diag.label.text()) == 'Enter the line sampling (Hz):'
		QTest.keyClicks(win_obj.diag.input_text, str(1800))
		assert win_obj.diag.input_text.text() == str(1800)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.line_sampling_win.isVisible() == False
		#Open the dialog for inputing the dwell time.
		assert win_obj.diag.dialog_dwell_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		assert str(win_obj.diag.label.text()) == 'Enter the pixel dwell time (us):'
		QTest.keyClicks(win_obj.diag.input_text, str(2.15))
		assert win_obj.diag.input_text.text() == str(2.15)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.dialog_dwell_win.isVisible() == False

		#assert win_obj.diag.use_settings_win.isVisible() == False
		#QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)
		#assert win_obj.diag.use_settings_win.isVisible() == False

		#Check that the line sampling dialog doesn't appear again.
		assert win_obj.diag.line_sampling_win.isVisible() == False

		#Check that the previous and next pane visualisation works well.
		QTest.mouseClick(win_obj.prev_pane, QtCore.Qt.LeftButton)
		for objId in par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				assert objId.pane == 0
				break;
		
		
		QTest.mouseClick(win_obj.bleach_corr1_btn, QtCore.Qt.LeftButton)

		assert win_obj.bleach_corr1_plugin.bleach_corr1_win.isVisible() == True
		
		assert win_obj.bleach_corr_on_off.text() == '  OFF  '
		QTest.mouseClick(win_obj.bleach_corr1_plugin.apply_corr_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.bleach_corr1_plugin.export_trace_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr_on_off.text() == 'M1 ON '

		print 'self.', np.sum(win_obj.bleach_corr1_plugin.objId.CH0_pc)




		win_obj.bleach_corr1_plugin.close()
		assert win_obj.bleach_corr1_plugin.bleach_corr1_win.isVisible() == False

		



		win_obj.test_path = [os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_with_PBC.tif']
		win_obj.test_path[0] = win_obj.test_path[0].replace('\\','/')

		QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
		win_obj.file_import.file_dialog.done(1,win_obj.test_path)

		#Open the dialog for the line sampling (Hz):
		assert win_obj.diag.line_sampling_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		assert str(win_obj.diag.label.text()) == 'Enter the line sampling (Hz):'
		QTest.keyClicks(win_obj.diag.input_text, str(1800))
		assert win_obj.diag.input_text.text() == str(1800)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.line_sampling_win.isVisible() == False
		#Open the dialog for inputing the dwell time.
		assert win_obj.diag.dialog_dwell_win.isVisible() == True
		assert win_obj.diag.input_text.isVisible() == True
		assert str(win_obj.diag.label.text()) == 'Enter the pixel dwell time (us):'
		QTest.keyClicks(win_obj.diag.input_text, str(2.15))
		assert win_obj.diag.input_text.text() == str(2.15)
		QTest.mouseClick(win_obj.diag.ok, QtCore.Qt.LeftButton)
		assert win_obj.diag.dialog_dwell_win.isVisible() == False

		#assert win_obj.diag.use_settings_win.isVisible() == False
		#QTest.mouseClick(win_obj.diag.no, QtCore.Qt.LeftButton)
		#assert win_obj.diag.use_settings_win.isVisible() == False

		#Check that the line sampling dialog doesn't appear again.
		assert win_obj.diag.line_sampling_win.isVisible() == False

		#Check that the previous and next pane visualisation works well.
		QTest.mouseClick(win_obj.prev_pane, QtCore.Qt.LeftButton)
		for objId in par_obj.objectRef:
			if(objId.cb.isChecked() == True):
				assert objId.pane == 0
				break;
		
		
		QTest.mouseClick(win_obj.bleach_corr1_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr1_plugin.bleach_corr1_win.isVisible() == True
		
		assert win_obj.bleach_corr_on_off.text() == '  OFF  '
		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH0_pc) == 0 
		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH1_pc) == 0
		QTest.mouseClick(win_obj.bleach_corr1_plugin.apply_corr_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.bleach_corr1_plugin.export_trace_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr_on_off.text() == 'M1 ON '

		
		#Check the carpet is modified by the photobleaching.

		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH0_pc) != 0 
		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH1_pc) != 0
		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH0_pc) != np.sum(win_obj.bleach_corr1_plugin.objId.CH0)
		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH1_pc) != np.sum(win_obj.bleach_corr1_plugin.objId.CH1)
		assert np.sum(win_obj.bleach_corr1_plugin.objId.CH1_pc) != np.sum(win_obj.bleach_corr1_plugin.objId.CH0_pc)

		win_obj.bleach_corr1_plugin.close()
		assert win_obj.bleach_corr1_plugin.bleach_corr1_win.isVisible() == False
		
		assert par_obj.numOfLoaded == 2
		for i in range(1,-1,-1):
			QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
		assert par_obj.numOfLoaded == 0
		
		

		
		


