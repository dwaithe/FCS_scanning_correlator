from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np

def test_scan_PB2_buttons(par_obj,win_obj):
	
		
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
		win_obj.test_path.append(os.getcwd()+'/test_files/1.msr')
		win_obj.test_path.append(os.getcwd()+'/test_files/2 (245Hz).msr')
		win_obj.test_path.append(os.getcwd()+'/test_files/3 (505 Hz).msr')
		win_obj.test_path.append(os.getcwd()+'/test_files/11 (mature, line 28).msr')

		for i in range(0, win_obj.test_path.__len__()):
			win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

		QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
		win_obj.file_import.file_dialog.done(1,win_obj.test_path)

		

		#Open the dialog for the line sampling (Hz):
		assert win_obj.diag.line_sampling_win.isVisible() == True, "Dialog for line sampling did not open."
		assert win_obj.diag.input_text.isVisible() == True, "Text input for line sampling did not open."
		assert str(win_obj.diag.label.text()) == 'Enter the line sampling (Hz):'
		QTest.keyClicks(win_obj.diag.input_text, str(404))
		assert win_obj.diag.input_text.text() == str(404)
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

		assert win_obj.diag.use_settings_win.isVisible() == True
		QTest.mouseClick(win_obj.diag.yes, QtCore.Qt.LeftButton)
		


		win_obj.diag.main_dialog_win.check1.click()
		QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
		assert win_obj.diag.isVisible() == False
		win_obj.diag.main_dialog_win.check1.click()
		QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
		assert win_obj.diag.isVisible() == False
		win_obj.diag.main_dialog_win.check1.click()
		QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
		assert win_obj.diag.isVisible() == False
		win_obj.diag.main_dialog_win.check1.click()
		QTest.mouseClick(win_obj.diag.main_dialog_win.button, QtCore.Qt.LeftButton)
		assert win_obj.diag.isVisible() == False

		
		#The following loads a collection of data which is too short etc... It shouldn't error, but you wouldn't use this data.
		
		QTest.mouseClick(win_obj.bleach_corr2_btn, QtCore.Qt.LeftButton)

		assert win_obj.bleach_corr2_plugin.bleach_corr2_win.isVisible() == True

		QTest.mouseClick(win_obj.bleach_corr2_plugin.preview_selection_btn, QtCore.Qt.LeftButton)
		win_obj.bleach_corr2_plugin.duration_combo.setCurrentIndex(3)

		QTest.mouseClick(win_obj.bleach_corr2_plugin.export_trace_btn, QtCore.Qt.LeftButton)

		QTest.mouseClick(win_obj.bleach_corr2_plugin.apply_to_all_data_btn, QtCore.Qt.LeftButton)


		#The last data file should work.
		assert win_obj.bleach_corr_on_off.text() == 'M2 ON '

		for i in range(4,-1,-1):
			QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
		assert par_obj.numOfLoaded == 0
		
		

		###Now we open a file and repeat the Photobleaching analysis on it several times. Used to produce an error.





		win_obj.test_path = [os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_numCH2_with_PBC.tif']


		for i in range(0, win_obj.test_path.__len__()):
			win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

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

		temp = np.copy(win_obj.carpet_img)

		QTest.mouseClick(win_obj.bleach_corr2_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr2_plugin.bleach_corr2_win.isVisible() == True
		QTest.mouseClick(win_obj.bleach_corr2_plugin.preview_selection_btn, QtCore.Qt.LeftButton)
		win_obj.bleach_corr2_plugin.duration_combo.setCurrentIndex(3)
		QTest.mouseClick(win_obj.bleach_corr2_plugin.export_trace_btn, QtCore.Qt.LeftButton)
		win_obj.bleach_corr2_plugin.close()
		
		#Switch on and off the correction.

		temp2 = np.copy(win_obj.carpet_img)
		assert np.sum(temp2) != np.sum(temp), "Your carpet didn't change subsequent to applying photobleaching."
		QTest.mouseClick(win_obj.bleach_corr_on_off, QtCore.Qt.LeftButton)
		temp3 = np.copy(win_obj.carpet_img)
		assert np.sum(temp3) == np.sum(temp), "Your carpet hasn't returned to normal by turning off the correction"
		QTest.mouseClick(win_obj.bleach_corr_on_off, QtCore.Qt.LeftButton)
		assert np.sum(temp2) != np.sum(temp), "Your carpet didn't change subsequent to applying photobleaching correction again."

		QTest.mouseClick(win_obj.bleach_corr2_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr2_plugin.bleach_corr2_win.isVisible() == True
		QTest.mouseClick(win_obj.bleach_corr2_plugin.preview_selection_btn, QtCore.Qt.LeftButton)
		#win_obj.bleach_corr2_plugin.duration_combo.setCurrentIndex(3)
		QTest.mouseClick(win_obj.bleach_corr2_plugin.export_trace_btn, QtCore.Qt.LeftButton)
		win_obj.bleach_corr2_plugin.close()

		temp2 = np.copy(win_obj.carpet_img)
		assert np.sum(temp2) != np.sum(temp), "Your carpet didn't change subsequent to applying photobleaching."
		QTest.mouseClick(win_obj.bleach_corr_on_off, QtCore.Qt.LeftButton)
		temp3 = np.copy(win_obj.carpet_img)
		assert np.sum(temp3) == np.sum(temp), "Your carpet hasn't returned to normal by turning off the correction"
		QTest.mouseClick(win_obj.bleach_corr_on_off, QtCore.Qt.LeftButton)
		assert np.sum(temp2) != np.sum(temp), "Your carpet didn't change subsequent to applying photobleaching correction again."



		##Now we can export the photobleached carpet and the unphotobleached carpet.

		QTest.mouseClick(win_obj.export_region_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.bleach_corr_on_off, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.export_region_btn, QtCore.Qt.LeftButton)


		for i in range(0,-1,-1):
			QTest.mouseClick(win_obj.xb[i], QtCore.Qt.LeftButton)
		assert par_obj.numOfLoaded == 0


