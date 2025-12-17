from PySide6.QtWidgets import QLabel, QSlider, QPushButton, QDialog
from PySide6.QtCore import QObject, Signal
from fsmc_settings import FSMC3Settings

class AxisUi(QObject):

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
		max = int(2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1
		self.sliderTarget.setMaximum(max)
		self.sliderTarget.setValue(int(max / 2))
		self.sliderTarget.setEnabled(True)
		self.labelTarget.setText(str(self.sliderTarget.value()))

	def pushTarget(self, value : str):
		self.labelTarget.setText(value)

	def updateTarget(self, value : str):
		self.labelTargetReported.setText(value)

	def loadCenterUi(self,
			btnNudgeUp_in : QPushButton,
			btnNudgeDown_in : QPushButton):
		self.btnNudgeUp = btnNudgeUp_in
		self.btnNudgeDown = btnNudgeDown_in

	def loadEnableUi(self,
			btnEnable_in: QPushButton,
			labelEnable_in: QLabel):
		self.btnEnable = btnEnable_in
		self.labelEnable = labelEnable_in
	
	def updateEnabled(self, value):
		if value >0:
			self.btnEnable.setText("Disable Axis")
			self.labelEnable.setText("Axis: Enabled")
		elif value <= 0:
			self.btnEnable.setText("Enable Axis")
			self.labelEnable.setText("Axis: Disabled")
