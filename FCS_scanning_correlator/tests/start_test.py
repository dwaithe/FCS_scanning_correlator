from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np
from test_msr_file_import import test_msr_file_import
from test_tiff_file_import import test_tiff_file_import
from test_lsm_file_import import test_lsm_file_import
from test_lif_file_import import test_lif_file_import
from test_scan_interface_buttons import test_scan_interface_buttons
from test_scan_PB1_buttons import test_scan_PB1_buttons
import warnings

def test_import_scripts():
	print 'testing'
	import sys
	sys.path.append('../')
	sys.path.append('../../../FCS_point/FCS_point_correlator/focuspoint')
	import scanningFCScorr as sfc


	win_tab, app,par_obj,win_obj,fit_obj = sfc.start_gui()
	win_obj.testing = True
	warnings.filterwarnings('ignore', '.*void CGSUpdateManager*',)
	
	#res0 = test_lsm_file_import(par_obj,win_obj)
	#res1 = test_msr_file_import(par_obj,win_obj)
	#res2 = test_lif_file_import(par_obj,win_obj)
	#res3 = test_tiff_file_import(par_obj,win_obj)
	#res4 = test_scan_interface_buttons(par_obj,win_obj)
	res5 = test_scan_PB1_buttons(par_obj,win_obj)

	win_tab.show()
	sys.exit(app.exec_())


if __name__ == '__main__':

	results = test_import_scripts()

