from PySide6.QtWidgets import QLabel, QSlider, QPushButton, QDialog
from PySide6.QtCore import QObject, Signal
from fsmc_settings import FSMC3Settings

class AxisUi(QObject):
	uiTargetChange = Signal(int, int)
	uiCenterNudge = Signal(int, int)
	uiEnableClicked = Signal(int, int)

	def __init__(self, index):
		super().__init__()
		self.index = index
		
		self.labelSPI		:	QLabel
		self.sliderSPI		:	QSlider
		self.labelABZ		:	QLabel
		self.sliderABZ		:	QSlider
		self.btnKp			:	QPushButton
		self.btnKi			:	QPushButton
		self.btnKd			:	QPushButton
		self.labelTarget	:	QLabel
		self.labelTargetReported	:	QLabel
		self.sliderTarget	:	QSlider
		self.btnNudgeUp		:	QPushButton
		self.btnNudgeDown	:	QPushButton
		self.btnEEPROMSave	:	QPushButton
		self.btnEEPROMLoad	:	QPushButton
		self.btnEEPROMWipe	:	QPushButton
		self.btnEnable		:	QPushButton
		self.labelEnable	:	QLabel

	def loadSPIUi(self,
			label : QLabel,
			slider : QSlider):
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
			label : QLabel,
			slider : QSlider):
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
			btnKp_in : QPushButton,
			btnKi_in : QPushButton,
			btnKd_in : QPushButton):
		self.btnKp = btnKp_in
		self.btnKi = btnKi_in
		self.btnKd = btnKd_in

	def updatePIDKp(self, value):
		self.btnKp.setText(str(value))

	def updatePIDKi(self, value):
		self.btnKi.setText(str(value))

	def updatePIDKd(self, value):
		self.btnKd.setText(str(value))

	def loadTargetUi(self,
			label : QLabel,
			slider : QSlider,
			labelReported : QLabel,):
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
			btnNudgeUp_in : QPushButton,
			btnNudgeDown_in : QPushButton):
		self.btnNudgeUp = btnNudgeUp_in
		self.btnNudgeDown = btnNudgeDown_in
		self.btnNudgeUp.clicked.connect(self.btnCenterNudgeUp)
		self.btnNudgeDown.clicked.connect(self.btnCenterNudgeDown)
	
	def btnCenterNudgeUp(self):
		self.uiCenterNudge.emit(self.index, 1)

	def btnCenterNudgeDown(self):
		self.uiCenterNudge.emit(self.index, -1)

	def loadEEPROMUi(self,
			btnSave_in: QPushButton,
			btnLoad_in: QPushButton,
			btnWipe_in: QPushButton):
		self.btnEEPROMSave = btnSave_in
		self.btnEEPROMLoad = btnLoad_in
		self.btnEEPROMWipe = btnWipe_in

	def loadEnableUi(self,
			btnEnable_in: QPushButton,
			labelEnable_in: QLabel):
		self.btnEnable = btnEnable_in
		self.labelEnable = labelEnable_in
	
	def updateEnabled(self, value):
		if value[self.index] >0:
			self.btnEnable.setText("Disable Axis")
			self.labelEnable.setText("Axis: Enabled")
		elif value[self.index] <= 0:
			self.btnEnable.setText("Enable Axis")
			self.labelEnable.setText("Axis: Disabled")

	def _updateTarget(self, value):
		self.labelTarget.setText(str(value))
		self.uiTargetChange.emit(self.index, value)