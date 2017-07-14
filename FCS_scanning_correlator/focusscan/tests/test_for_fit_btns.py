from PyQt4.QtTest import QTest
from PyQt4 import QtGui, QtCore
import os
import numpy as np

def test_for_fit_btns(par_obj,win_obj,fit_obj):
		print 'testing'

		#self.main_frame = QWidget()
		
		#self.fig
		#self.canvas
		


		

		#self.mpl_toolbar
		
		
		#self.series_list_view 
		#self.to_spin
		#self.series_list_view2

		#############The left panel.
		
		#self.load_box
		#QTest.mouseClick(fit_obj.load_corr_file_btn, QtCore.Qt.LeftButton)
		#QTest.mouseClick(fit_obj.load_folder_btn, QtCore.Qt.LeftButton)
		QTest.mouseClick(fit_obj.on_about_btn, QtCore.Qt.LeftButton)
		fit_obj.about_win.close()

		"""
	
		
		

		self.model_layout = QHBoxLayout()
		self.model_layout.setSpacing(16)
		
		#Drop down list of equations for diffusing species
		self.diffModEqSel = comboBoxSp2(self);
		self.diffModEqSel.setToolTip('Set the type of equation to fit (see documentation for more advice).')
		self.diffModEqSel.type ='Diff_eq'
		self.diffModEqSel.addItem('Equation 1A')
		self.diffModEqSel.addItem('Equation 1B')
		self.diffModEqSel.addItem('GS neuron')
		self.diffModEqSel.addItem('Vesicle Diffusion')
		self.diffModEqSel.addItem('PB Correction')
		self.model_layout.addWidget(self.diffModEqSel)



		#Spin box for number of diffusing species
		diffNumSpecies = QHBoxLayout()
		diffNumSpecies.setSpacing(16)
		diffNumSpecLabel = QLabel('Num. of: diffusing species')
		diffNumSpecLabel.setToolTip('Set the number of diffusing species to be included in the fitting.')


		self.diffNumSpecSpin = QSpinBox()
		self.diffNumSpecSpin.setRange(1,3);
		self.diffNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(diffNumSpecLabel)
		diffNumSpecies.addWidget(self.diffNumSpecSpin)

		
		#Drop down list of equations for Triplet equations
		self.tripModEqSel = comboBoxSp2(self);
		self.tripModEqSel.setToolTip('Set the number of Triplet states to be included in the fitting')
		self.tripModEqSel.type ='Triplet_eq'
		self.tripModEqSel.addItem('no triplet')
		self.tripModEqSel.addItem('Triplet Eq 2A')
		self.tripModEqSel.addItem('Triplet Eq 2B')

		self.model_layout.addWidget(self.tripModEqSel)
		#Drop down box for selecting 2D or 3D model:
		self.dimenModSel = comboBoxSp2(self)
		self.dimenModSel.setToolTip('Set the dimensionality of the equation for fitting.')
		self.dimenModSel.type ='Dimen'
		self.dimenModSel.addItem('2D')
		self.dimenModSel.addItem('3D')
		self.model_layout.addWidget(self.dimenModSel)
		self.model_layout.addStretch()
		#Drop-down list with all the available models.
		
		#Spin box for number of diffusing species
		
		tripNumSpecLabel = QLabel('Triplet states')
		self.tripNumSpecSpin = QSpinBox()
		self.tripNumSpecSpin.setRange(1,3);
		self.tripNumSpecSpin.valueChanged[int].connect(self.updateParamFirst)
		diffNumSpecies.addWidget(tripNumSpecLabel)
		diffNumSpecies.addWidget(self.tripNumSpecSpin)
		diffNumSpecies.addStretch()
		




		self.modelFitSel = comboBoxSp2(self)
		self.modelFitSel.type = 'Fit'

		fit_layout = QHBoxLayout()
		fit_layout.setSpacing(16)
		

		
		self.fit_btn_min_label = QLabel("Fit from:")
		self.fit_btn_min = spinBoxSp3(self)
		self.fit_btn_min.setToolTip("Sets the position of the lower limit handle for the data fitting")
		self.fit_btn_min.type ='min'
		self.fit_btn_min.setMaximumWidth(90)
		self.fit_btn_min.setDecimals = 3
		self.fit_btn_min.valueChanged.connect(self.fit_btn_min.onEdit)
		

		self.fit_btn_max_label = QLabel("to:")
		self.fit_btn_max = spinBoxSp3(self)
		self.fit_btn_min.setToolTip("Sets the position of the upper limit handle for the data fitting")
		self.fit_btn_max.type ='max'
		self.fit_btn_max.setMaximumWidth(90)
		self.fit_btn_max.setDecimals = 3
		self.fit_btn_max.valueChanged.connect(self.fit_btn_max.onEdit)


		#Profile panel for different buttons.
		default_profile_panel = QHBoxLayout()
		default_profile_panel.setSpacing(16)

		text_default_profile = QLabel('Profile:')

		load_default_profile = QPushButton('load')
		load_default_profile.setToolTip('Will open a dialog to load a previously saved paramter fit profile')
		self.load_default_profile_output = folderOutput(self)
		self.load_default_profile_output.type = 'profile_load'
		
		save_default_profile = QPushButton('save')
		save_default_profile.setToolTip('Will open a dialog to save a parameter profile for the fitting')
		self.save_default_profile_output = folderOutput(self)
		self.save_default_profile_output.type = 'profile_save'

		store_default_profile = QPushButton('store')
		store_default_profile.setToolTip('Allows you to temporary store a parameter fit profile')
		apply_default_profile = QPushButton('apply')
		store_default_profile.setToolTip('Allows you to apply a parameter fit profile which has been previously loaded or stored')
		
		default_profile_panel.addWidget(text_default_profile)
		default_profile_panel.addWidget(load_default_profile)
		default_profile_panel.addWidget(save_default_profile)
		default_profile_panel.addWidget(store_default_profile)
		default_profile_panel.addWidget(apply_default_profile)
		default_profile_panel.addStretch()

		
		save_default_profile.clicked.connect(self.save_default_profile_fn)
		load_default_profile.clicked.connect(self.load_default_profile_fn)
		store_default_profile.clicked.connect(self.store_default_profile_fn)
		apply_default_profile.clicked.connect(self.apply_default_profile_fn)


		
		
		
		

		
			#Table which has the fitting
		self.fitTable = QTableWidget()


		

		
		#self.fitTable.setMinimumWidth(320)
		self.fitTable.setMaximumWidth(400)
		self.fitTable.setMinimumHeight(100)
		self.fitTable.setMaximumHeight(600)
		
		
		
		self.fit_btn = QPushButton("Current")
		self.fit_btn.clicked.connect(self.fit_equation)
		self.fit_btn.setToolTip('This will fit the data selected in the \"Display Model Parameters\" drop-down list.')


		self.fitAll_btn = QPushButton("All")
		self.fitAll_btn.setToolTip('This will fit all the data in the \"Data Series Viewer\" ')
		self.fitAll_btn.clicked.connect(self.fitAll_equation)

		#Horizontal Layout for fit_btns.
		fit_btns = QHBoxLayout()
		fit_btns.setSpacing(16)
		
		#Fit components
		self.fit_btn_txt = QLabel("Fit with param: ")
		self.fitSelected_btn = QPushButton("Only highlighted")
		self.fitSelected_btn.setToolTip("This will fit data which is highlighted in the \"Data Series Viewer\"")
		self.fitSelected_btn.clicked.connect(self.fitSelected_equation)

		#Fit button adding to layout.
		fit_btns.addWidget(self.fit_btn_txt)
		fit_btns.addWidget(self.fit_btn)
		fit_btns.addWidget(self.fitAll_btn)
		fit_btns.addWidget(self.fitSelected_btn)
		fit_btns.addStretch();

		#bootstrap.
		bootstrap_panel = QHBoxLayout()
		bootstrap_panel.setSpacing(16)
		bootstrap_panel.addSpacing(200)

		self.bootstrap_enable_toggle = False
		self.bootstrap_enable_btn = QPushButton('OFF')
		self.bootstrap_enable_btn.setStyleSheet("color: red");
		self.bootstrap_enable_btn.setFixedWidth(60)
		self.bootstrap_enable_btn.clicked.connect(self.bootstrap_enable_toggle_fn)
		self.bootstrap_enable_btn.setToolTip('This will enable bootstapping (see documentation formore details)')
		self.bootstrap_samples = QSpinBox()
		self.bootstrap_samples.setRange (1,400)
		self.bootstrap_samples.setValue(100)
		self.bootstrap_samples.setToolTip('This number represents the quantity of bootstrap samples to use.')

		bootstrap_panel.addWidget(QLabel('bootstrap:'))
		bootstrap_panel.addWidget(self.bootstrap_enable_btn)
		bootstrap_panel.addWidget(self.bootstrap_samples)
		bootstrap_panel.addStretch()
		
		



		
		
		modelFitSel_box = QHBoxLayout()
		modelFitSel_box.setSpacing(16)
		self.modelFitSel_label = QLabel('Display model parameters for data:')
		modelFitSel_box.addWidget(self.modelFitSel_label)
		modelFitSel_box.addStretch()


		#main left panel layout.
		left_vboxTop = QVBoxLayout()
		left_vboxMid = QVBoxLayout()
		left_vboxBot = QVBoxLayout()
		
		left_vboxTop.setContentsMargins(0,0,0,0)
		left_vboxTop.setSpacing(2)
		left_vboxMid.setContentsMargins(0,0,0,0)
		left_vboxMid.setSpacing(2)
		left_vboxBot.setContentsMargins(0,0,0,0)
		left_vboxBot.setSpacing(2)
		#self.load_box.setContentsMargins(0,0,0,0)
		#self.load_box.setSpacing(16)
		#left_vboxBot.setSpacing(0.5)
		#self.load_box.setSpacing(0.5)
		left_vboxTop.addLayout(self.load_box)
		left_vboxTop.addLayout(self.model_layout) 
		left_vboxTop.addLayout(diffNumSpecies) 
		
		left_vboxTop.addLayout(modelFitSel_box)
		
		left_vboxTop.addWidget(self.modelFitSel)
		left_vboxTop.addLayout(fit_btns)
		if self.type == 'scan':
			left_vboxTop.addLayout(bootstrap_panel)
		left_vboxTop.addLayout(fit_layout)
		
		left_vboxTop.addLayout(default_profile_panel)
		left_vboxTop.addSpacing(4)
		left_vboxTop.addWidget(self.fitTable)
		left_vboxTop.addSpacing(4)
		left_vboxTop.setAlignment(QtCore.Qt.AlignLeft)

		
		
		fit_layout.addWidget(self.fit_btn)
		fit_layout.addWidget(self.fit_btn_min_label)
		fit_layout.addWidget(self.fit_btn_min)
		fit_layout.addWidget(self.fit_btn_max_label)
		fit_layout.addWidget(self.fit_btn_max)
		fit_layout.addStretch()


		
		
		#left_vbox.addWidget(self.fitSelected_btn)
		#left_vbox.addWidget(self.saveOutput_btn)

		
		#Copy Fit parameters and the raw data inc. fit.
		copy_text = QLabel("Copy: ")
		self.copy_output_btn = QPushButton("parameters")
		self.copy_output_btn.setToolTip("Copies the fit parameters to the clipboard.")
		self.copy_output_btn.clicked.connect(self.copyOutputDataFn)
		self.copy_model_btn = QPushButton("plot data")
		self.copy_model_btn.setToolTip("Copies the raw data and fit data to the clipboard.");
		self.copy_model_btn.clicked.connect(self.copyModelFile)

		copy_layout = QHBoxLayout()
		copy_layout.setSpacing(16)
		copy_layout.addWidget(copy_text)
		copy_layout.addWidget(self.copy_output_btn)
		copy_layout.addWidget(self.copy_model_btn)
		copy_layout.addStretch();

		

		#Save Fit parameters and the raw data inc. fit.
		save_text = QLabel("Save: ")
		self.save_output_btn = QPushButton("parameters")
		self.save_output_btn.setToolTip("Saves the learnt parameters to a file.")
		self.save_output_btn.clicked.connect(self.saveOutputDataFn)
		
		self.save_model_btn = QPushButton("plot data")
		self.save_model_btn.setToolTip("Saves the raw data and fit data to a file.");
		self.save_model_btn.clicked.connect(self.saveModelFile)

		save_layout = QHBoxLayout()
		save_layout.setSpacing(16)
		save_layout.addWidget(save_text)
		save_layout.addWidget(self.save_output_btn)
		save_layout.addWidget(self.save_model_btn)
		save_layout.addStretch()


		output_layout = QHBoxLayout()
		output_layout.setSpacing(16)
		self.fileNameText = QLineEdit('outputFileName')
		

		self.folderSelect_btn = QPushButton('Output Folder')
		self.folderSelect_btn.setToolTip('Select the output folder for saving the files to.')
		self.folderOutput = folderOutput(self)
		self.folderOutput.type = 'output_dir'
		self.folderSelect_btn.clicked.connect(self.folderOutput.showDialog)

		output_layout.addWidget(self.fileNameText)
		output_layout.addWidget(self.folderSelect_btn)
		output_layout.addStretch()

		left_vboxBot.addSpacing(12)
		left_vboxBot.addLayout(copy_layout)
		left_vboxBot.addLayout(save_layout)
		left_vboxBot.addLayout(output_layout)
		
		

		
		left_vboxBot.addStretch()

		left_vbox = QVBoxLayout()
		left_vbox.setContentsMargins(0,0,0,0)
		left_vbox.setSpacing(16)

		left_stretch = QSplitter(QtCore.Qt.Vertical)
		left_vboxTopWid = QWidget()
		left_vboxBotWid = QWidget()
		
		left_vboxTopWid.setLayout(left_vboxTop)
		left_vboxBotWid.setLayout(left_vboxBot)

		left_stretch.addWidget(left_vboxTopWid)
		left_stretch.addWidget(left_vboxBotWid)
		left_vbox.addWidget(left_stretch)

		center_vbox = QVBoxLayout()
		center_vbox.addWidget(self.canvas)
		center_vbox.addWidget(self.mpl_toolbar)
		resetScale = QPushButton("Reset Scale")
		resetScale.setToolTip('Will reset the scale to be the bounds of the plot with the largest amplitude')
		resetScale.clicked.connect(self.resetScaleFn)
		
		self.turnOffAutoScale = QPushButton("Keep Scale")
		self.turnOffAutoScale.setToolTip("Will stop the scale from dynamically changeing.")
		self.turnOffAutoScale.setCheckable(True)
		self.turnOffAutoScale.clicked.connect(self.autoScaleFn)

		self.norm_to_one_btn = QPushButton("Normalize Function")
		self.norm_to_one_btn.setToolTip("Will ensure all curves scale between 1.0 and 0.0")
		self.norm_to_one_btn.setCheckable(True)
		self.norm_to_one_btn.clicked.connect(self.norm_to_one_fn)
		
		center_hbox = QHBoxLayout()
		center_hbox.setSpacing(16)
		center_vbox.addLayout(center_hbox)
		center_hbox.addWidget(resetScale)
		center_hbox.addWidget(self.turnOffAutoScale)
		center_hbox.addWidget(self.norm_to_one_btn)
		center_hbox.setAlignment(QtCore.Qt.AlignLeft)


		right_vbox = QVBoxLayout()
		right_vbox.addWidget(log_label)
		right_vbox.addWidget(self.series_list_view)
		self.series_list_view.setMinimumWidth(260)
		self.series_list_view.setMinimumHeight(260)
		#right_vbox.addLayout(spins_hbox)

		legend_box = QHBoxLayout()
		legend_box.setSpacing(16)
		#self.legend_cb = QCheckBox("Show L&egend")
		#self.legend_cb.setChecked(False)
		#legend_box.addWidget(self.legend_cb)
		

		self.right_check_all_none = QPushButton("check all")
		self.show_button = QPushButton("Plot Checked Data")
		
		self.switch_true_false = True



		legend_box.addWidget(self.show_button)
		legend_box.addWidget(self.right_check_all_none)
		right_vbox.addLayout(legend_box)

		right_ch_check = QHBoxLayout()
		right_ch_check.setSpacing(16)
		#Channel 0 auto-correlation
		ch_check_ch0_label = QLabel("ac: CH0")
		self.ch_check_ch0 = QCheckBox()
		self.ch_check_ch0.setChecked(True)
		self.ch_check_ch0.setToolTip("check to display CH0 auto-correlation data.")
		self.ch_check_ch0.stateChanged.connect(self.fill_series_list)
		#Channel 1 auto-correlation
		ch_check_ch1_label = QLabel("CH1")
		self.ch_check_ch1 = QCheckBox()
		self.ch_check_ch1.setChecked(True)
		self.ch_check_ch1.setToolTip("check to display CH1 auto-correlation data.")
		self.ch_check_ch1.stateChanged.connect(self.fill_series_list)
		#Channel 01 cross-correlation
		ch_check_ch01_label = QLabel("cc: CH01")
		self.ch_check_ch01 = QCheckBox()
		self.ch_check_ch01.setChecked(True)
		self.ch_check_ch01.setToolTip("check to display CH01 cross-correlation data.")
		self.ch_check_ch01.stateChanged.connect(self.fill_series_list)
		#Channel 10 cross-correlation
		ch_check_ch10_label = QLabel("CH10")
		self.ch_check_ch10 = QCheckBox()
		self.ch_check_ch10.setChecked(False)
		self.ch_check_ch10.setToolTip("check to display CH10 cross-correlation data.")
		self.ch_check_ch10.stateChanged.connect(self.fill_series_list)
		#Add widgets.
		right_ch_check.addWidget(ch_check_ch0_label)
		right_ch_check.addWidget(self.ch_check_ch0)
		right_ch_check.addWidget(ch_check_ch1_label)
		right_ch_check.addWidget(self.ch_check_ch1)
		right_ch_check.addWidget(ch_check_ch01_label)
		right_ch_check.addWidget(self.ch_check_ch01)
		right_ch_check.addWidget(ch_check_ch10_label)
		right_ch_check.addWidget(self.ch_check_ch10)
		#Add to main layout.
		self.right_check_all_none.clicked.connect(self.check_all_none)
		self.connect(self.show_button, QtCore.SIGNAL('clicked()'), self.on_show)
		right_vbox.addLayout(right_ch_check)

		

		right_vbox.addWidget(self.right_check_all_none)
		
		self.chi_limit_label = QLabel('chi^2 cut-off value')
		self.chi_limit = QDoubleSpinBox()
		self.chi_limit.setToolTip('The Data Series Viewer cut-off. Fits with chi^2 above this value will be red, lower geen.')
		self.chi_limit.setMinimum(0)
		self.chi_limit.setDecimals(3)
		self.chi_limit.setMaximum(99.999)
		self.chi_limit.setSingleStep(0.001)
		self.chi_limit.setValue(self.chisqr)
		self.chi_limit.valueChanged.connect(self.chi_limit_update)
		chi_limit_box = QHBoxLayout()
		chi_limit_box.addStretch()
		chi_limit_box.addWidget(self.chi_limit_label)
		chi_limit_box.addWidget(self.chi_limit)

		self.remove_btn = QPushButton("Remove Highlighted Data")
		self.remove_btn.setToolTip('Remove highlighted data from \"Data Series Viewer\" ')
		self.remove_btn.clicked.connect(self.removeDataFn)
		self.create_average_btn = QPushButton("Create average of Highlighted")
		self.create_average_btn.setToolTip('Creates a new average plot from any plots highlighted in the \"Data Series Viewer\" ')
		self.create_average_btn.clicked.connect(self.create_average_fn)
		self.clearFits_btn = QPushButton("Clear Fit Data All/Highlighted")
		self.clearFits_btn.setToolTip('Clears the fit parameters only from any data-files highlighted in the \"Data Series Viewer\" ')
		self.clearFits_btn.clicked.connect(self.clearFits)
		self.visual_histo = visualHisto(self)
		visual_histo_btn = QPushButton("Generate Histogram");
		visual_histo_btn.setToolTip('Opens the Generate Histogram plot dialog')
		visual_histo_btn.clicked.connect(self.visual_histo.create_main_frame)
		self.visual_scatter = visualScatter(self)
		visual_scatter_btn = QPushButton("Generate Scatter");
		visual_histo_btn.setToolTip('Opens the Generate Scatter plot dialog')
		visual_scatter_btn.clicked.connect(self.visual_scatter.create_main_frame)

		right_vbox.addLayout(chi_limit_box)
		right_vbox.addWidget(self.remove_btn)
		right_vbox.addWidget(self.create_average_btn)
		right_vbox.addWidget(self.clearFits_btn)
		right_vbox.addWidget(visual_histo_btn)
		right_vbox.addWidget(visual_scatter_btn)
		right_vbox.addStretch(1)

		filter_box = QHBoxLayout()
		right_vbox.addLayout(filter_box)


		self.tfb = TableFilterBox(self)


		filter_box.addWidget(self.tfb)
		self.filter_add_panel = QHBoxLayout()
		self.filter_select = QComboBox()
		self.filter_select.setMaximumWidth(100)
		self.filter_select.setToolTip('Specifies parameter of fit to filter')
		

		for item in self.def_param:
			self.filter_select.addItem(item)

		self.filter_lessthan = QComboBox()
		self.filter_lessthan.addItem('<')
		self.filter_lessthan.addItem('>')
		self.filter_lessthan.setToolTip("Species direction of filter")
		self.filter_lessthan.setMaximumWidth(50)
		self.filter_value = QLineEdit('10.0')
		self.filter_value.setMaximumWidth(50)
		self.filter_value.setMinimumWidth(50)
		self.filter_add = QPushButton('add')
		self.filter_add.setToolTip('Will add a filter which processes the data in the \"Data Series Viewer\"')
		self.filter_add_panel.addWidget(self.filter_select)
		self.filter_add_panel.addWidget(self.filter_lessthan)
		self.filter_add_panel.addWidget(self.filter_value)
		self.filter_add_panel.addWidget(self.filter_add)
		right_vbox.addLayout(self.filter_add_panel)
		

		self.filter_add.clicked.connect(self.tfb.filter_add_fn)
		hbox = QHBoxLayout()
		splitter = QSplitter();
		
		hbox1 =QWidget()
		hbox1.setLayout(left_vbox)
		hbox2 =QWidget()
		hbox2.setLayout(center_vbox)
		hbox3 = QWidget()
		hbox3.setLayout(right_vbox)
		#hbox.addLayout(right_vbox)
		splitter.addWidget(hbox1)
		splitter.addWidget(hbox2)
		splitter.addWidget(hbox3)
		#Splitter instance. Can't have 
		
		container = QWidget()

		self.image_status_text = QStatusBar()
		
		self.image_status_text.showMessage("Please load a data file. ")
		self.image_status_text.setStyleSheet("QLabel {  color : green }")
		left_vbox.addWidget(self.image_status_text)

		hbox.addWidget(splitter)
		self.defineTable()
		self.main_frame.setLayout(hbox)
		"""