from PySide6 import QtWidgets as qtw
from PySide6.QtCore import QObject, Signal
from fsmc_settings import FSMC3Settings

class AxisUi(QObject):
	uiTargetChange = Signal(int, int)
	uiCenterNudge = Signal(int, int)

	def __init__(self, index):
		super().__init__()
		self.index = index
		
		self.labelSPI		:	qtw.QLabel
		self.sliderSPI		:	qtw.QSlider
		self.labelABZ		:	qtw.QLabel
		self.sliderABZ		:	qtw.QSlider
		self.labelKp		:	qtw.QLabel
		self.labelKi		:	qtw.QLabel
		self.labelKd		:	qtw.QLabel
		self.labelTarget	:	qtw.QLabel
		self.labelTargetReported	:	qtw.QLabel
		self.sliderTarget	:	qtw.QSlider
		self.btnNudgeUp		:	qtw.QPushButton
		self.btnNudgeDown	:	qtw.QPushButton
		self.btnEEPROMSave	:	qtw.QPushButton
		self.btnEEPROMLoad	:	qtw.QPushButton
		self.btnEEPROMWipe	:	qtw.QPushButton
		self.btnEnable		:	qtw.QPushButton
		self.labelEnable	:	qtw.QLabel

	def loadSPIUi(self,
			label : qtw.QLabel,
			slider : qtw.QSlider):
		self.labelSPI = label
		self.sliderSPI = slider
		self.sliderSPI.setMaximum(int(2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1)
		self.sliderSPI.setEnabled(False)

	def updateSPIUi(self, value : int):
		try:
			self.sliderSPI.setValue(value[self.index])
			self.labelSPI.setText(str(value[self.index]))
		except Exception as err:
			print("updateSPIUi: " + err)

	def loadABZUi(self,
			label : qtw.QLabel,
			slider : qtw.QSlider):
		self.labelABZ = label
		self.sliderABZ = slider
		self.sliderABZ.setMaximum(int(2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1)
		self.sliderABZ.setEnabled(False)

	def updateABZUi(self, value):
		try:
			self.sliderABZ.setValue(value[self.index])
			self.labelABZ.setText(str(value[self.index]))
		except Exception as err:
			print("updateABZUi: " + err)

	def loadPIDUi(self,
			labelKp_in : qtw.QLabel,
			labelKi_in : qtw.QLabel,
			labelKd_in : qtw.QLabel):
		self.labelKp = labelKp_in
		self.labelKi = labelKi_in
		self.labelKd = labelKd_in

	def updatePIDKp(self, value):
		self.labelKp.setText(str(value))

	def updatePIDKi(self, value):
		self.labelKi.setText(str(value))

	def updatePIDKd(self, value):
		self.labelKd.setText(str(value))

	def loadTargetUi(self,
			label : qtw.QLabel,
			slider : qtw.QSlider,
			labelReported : qtw.QLabel,):
		self.labelTarget = label
		self.sliderTarget = slider
		self.labelTargetReported = labelReported
		self.sliderTarget.valueChanged.connect(self._updateTarget)
		max = int(2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1
		self.sliderTarget.setMaximum(max)
		self.sliderTarget.setValue(int(max / 2))
		self.sliderTarget.setEnabled(True)
		self.sliderTarget.valueChanged.connect(self.sliderTargetFromUiChange)

	def updateTargetReportedUi(self, value):
		self.labelTargetReported.setText(str(value[self.index]))
	
	def sliderTargetFromUiChange(self, value):
		self.uiTargetChange.emit(self.index, value)

	def loadCenterUi(self,
			btnNudgeUp_in : qtw.QPushButton,
			btnNudgeDown_in : qtw.QPushButton):
		self.btnNudgeUp = btnNudgeUp_in
		self.btnNudgeDown = btnNudgeDown_in
		self.btnNudgeUp.clicked.connect(self.btnCenterNudgeUp)
		self.btnNudgeDown.clicked.connect(self.btnCenterNudgeDown)
	
	def btnCenterNudgeUp(self):
		self.uiCenterNudge.emit(self.index, 1)

	def btnCenterNudgeDown(self):
		self.uiCenterNudge.emit(self.index, -1)

	def loadEEPROMUi(self,
			btnSave_in: qtw.QPushButton,
			btnLoad_in: qtw.QPushButton,
			btnWipe_in: qtw.QPushButton):
		self.btnEEPROMSave = btnSave_in
		self.btnEEPROMLoad = btnLoad_in
		self.btnEEPROMWipe = btnWipe_in

	def loadEnableUi(self,
			btnEnable_in: qtw.QPushButton,
			labelEnable_in: qtw.QLabel):
		self.btnEnable = btnEnable_in
		self.labelEnable = labelEnable_in

	def _updateTarget(self, value):
		self.labelTarget.setText(str(value))
		self.uiTargetChange.emit(self.index, value)