from PyQt5.QtTest import QTest
from PyQt5 import QtGui, QtCore
import os
import numpy as np

def test_scan_interface_buttons(par_obj,win_obj):
	
		
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
		
		
		win_obj.test_path = [os.getcwd()+'/test_files/out_img_D_0p2_noi_0_drift_False_ts_30000_mol_120_bleach_False_prob_0_4_.tif']
		for i in range(0, win_obj.test_path.__len__()):
			win_obj.test_path[i] = win_obj.test_path[i].replace('\\','/')

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
		
		QTest.mouseClick(win_obj.next_pane, QtCore.Qt.LeftButton)
		assert objId.pane == 1
		QTest.mouseClick(win_obj.prev_pane, QtCore.Qt.LeftButton)
		assert objId.pane == 0

		QTest.mouseClick(win_obj.crop_data_btn, QtCore.Qt.LeftButton)
		assert win_obj.crop_data_win.crop_window.isVisible() == True
		assert win_obj.crop_data_win.crop_panel.title() == 'Import Crop Settings'
		win_obj.crop_data_win.close()
		assert win_obj.crop_data_win.crop_window.isVisible() == False

		QTest.mouseClick(win_obj.bleach_corr1_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr1_plugin.bleach_corr1_win.isVisible() == True
		win_obj.bleach_corr1_plugin.close()
		assert win_obj.bleach_corr1_plugin.bleach_corr1_win.isVisible() == False

		QTest.mouseClick(win_obj.bleach_corr2_btn, QtCore.Qt.LeftButton)
		assert win_obj.bleach_corr2_plugin.bleach_corr2_win.isVisible() == True
		win_obj.bleach_corr2_plugin.close()
		assert win_obj.bleach_corr2_plugin.bleach_corr2_win.isVisible() == False

		assert par_obj.numOfLoaded == 1
		
		QTest.mouseClick(win_obj.xb[0], QtCore.Qt.LeftButton)
		assert par_obj.numOfLoaded == 0


		"""#win_obj.toolbar1 
		#win_obj.label 
		#win_obj.fileDialog 
		#win_obj.toolbar2 
		QTest.mouseClick(win_obj.prev_pane, QtCore.Qt.LeftButton)	
		QTest.mouseClick(win_obj.next_pane, QtCore.Qt.LeftButton)
		#win_obj.file_import 
		QTest.mouseClick(win_obj.import_adv_btn, QtCore.Qt.LeftButton) 
		QTest.mouseClick(win_obj.imp_adv_win, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.reprocess_btn, QtCore.Qt.LeftButton)
		#win_obj.mText
		#win_obj.DeltatText
		#win_obj.DeltatEdit
		#win_obj.spatialBinText
		#win_obj.spatialBinEdit 
		QTest.mouseClick(win_obj.bleachCorr1_btn, QtCore.Qt.LeftButton) 
		QTest.mouseClick(win_obj.bleachCorr1_on_off, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.bleachCorr2_btn, QtCore.Qt.LeftButton)
		#win_obj.displayCarpetText
		QTest.mouseClick(win_obj.CH0Auto_btn , QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.CH1Auto_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.CH01Cross_btn, QtCore.Qt.LeftButton) 
		#win_obj.displayExportText
		QTest.mouseClick(win_obj.addRegion_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.clear_region_btn, QtCore.Qt.LeftButton)
		#QTest.mouseClick(win_obj.folderOutput, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.folderSelect_btn, QtCore.Qt.LeftButton) 
		#win_obj.save_corr_txt
		QTest.mouseClick(win_obj.save_corr_carpet_btn, QtCore.Qt.LeftButton) 
		QTest.mouseClick(win_obj.save_log_corr_carpet_btn, QtCore.Qt.LeftButton)
		#QTest.mouseClick(win_obj.spot_size_calc
		#QTest.mouseClick(win_obj.spot_size_calc_plugin 
		QTest.mouseClick(win_obj.export_all_data_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.export_region_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(win_obj.export_all_data_to_csv_btn, QtCore.Qt.LeftButton)
		"""
		
		
		
		
		
		

		
		


