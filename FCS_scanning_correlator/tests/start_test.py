from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os

def test_import_scripts():
	print 'testing'
	import sys
	sys.path.append('../')
	sys.path.append('../../../FCS_point/FCS_point_correlator/focuspoint')
	import scanningFCScorr as sfc


	win_tab, app,par_obj,win_obj,fit_obj = sfc.start_gui()


	#win_obj.ex.showDialog()
	win_obj.testing = True
	win_obj.test_path = [os.getcwd()+'/test_files/1.msr']
	QTest.mouseClick(win_obj.openFile, QtCore.Qt.LeftButton)
	win_obj.testWin.check1.click()
	QTest.mouseClick(win_obj.testWin.button, QtCore.Qt.LeftButton)

	
	#path = 'test_files/'
	#filename = '20140902_ScanFCCS_Jcam Glass LCksnap STAR Sri.lif'
	#par_obj.gui  ='show'
	#filepath = path+filename
	#scanlist = Import_lif(filepath,par_obj, mainWin)
	#c=0
	#selList =[];
	#for name in scanlist.store:
#		c = c+1

		#exec("boolV = self.check"+str(c)+".isChecked()");
#		if c == 3:
#			selList.append(name)
#	print selList.__len__()
#	scanlist.import_lif_sing(selList)
#	mainWin.testWin.close()
#	mainWin.plotDataQueueFn()

	#win_tab.show()
	#Starts the display app.exec_()
	#sys.exit(app.exec_())
	

	return False



if __name__ == '__main__':

	assert(test_import_scripts())
