from PySide6 import QtWidgets as qtw
from PySide6.QtCore import QObject, SignalInstance, Signal
from structure.AxisUi import AxisUi
from fsmc_settings import FSMC3Settings

class Axis(QObject):
	uiCommandOutput = Signal(str, int, int)

	def __init__(self, index):
		super().__init__()
		self.index				=	index
		self._ui				=	AxisUi(index)
		self._communicator		=	None
		self.posSPI 	:	int	=	0
		self.posABZ 	:	int	=	0
		self.tuneP 		:	int	=	0
		self.tuneI 		:	int	=	0
		self.tuneD 		:	int	=	0
		self.posCmdTarget	:	int	=	0
		self.posDevTarget	:	int	=	0

	def loadSPI(self,
			signal : SignalInstance,
			label : qtw.QLabel,
			slider : qtw.QSlider):
		signal.connect(self.updateSPI)
		self._ui.loadSPIUi(label, slider)

	def updateSPI(self, value):
		try:
			self.posSPI = value
			self._ui.updateSPIUi(value)
		except Exception as err:
			print("updateSPI: " + str(err))

	def loadABZ(self,
			signal : SignalInstance,
			label : qtw.QLabel,
			slider : qtw.QSlider):
		signal.connect(self.updateABZ)
		self._ui.loadABZUi(label, slider)

	def updateABZ(self, value):
		try:
			self.posABZ = value
			self._ui.updateABZUi(value)
		except Exception as err:
			print("updateABZ: " + str(err))

	def loadPID(self,
			signal : SignalInstance,
			labelKp_in : qtw.QLabel,
			labelKi_in : qtw.QLabel,
			labelKd_in : qtw.QLabel):
		signal.connect(self.updatePID)
		self._ui.loadPIDUi(labelKp_in, labelKi_in, labelKd_in)

	def updatePID(self, payload):
		tuneName = payload[self.index][0]
		tuneValue = payload[self.index][1]
		try:
			if tuneName == "p":
				truncVal = f"{tuneValue:.{3}f}"
				self._ui.updatePIDKp(truncVal)
			if tuneName == "i":
				truncVal = f"{tuneValue:.{4}f}"
				self._ui.updatePIDKi(truncVal)
			if tuneName == "d":
				truncVal = f"{tuneValue:.{4}f}"
				self._ui.updatePIDKd(truncVal)
		except Exception as err:
			print("updatePID: " + err)

	def loadTarget(self,
			signal : Signal,
			label : qtw.QLabel,
			slider : qtw.QSlider,
			labelReported : qtw.QLabel,):
		self._ui.loadTargetUi(label, slider, labelReported)
		self._ui.uiTargetChange.connect(self.updateTargetFromUi)
		signal.connect(self._ui.updateTargetReportedUi)
	
	def updateTargetFromUi(self, index, value):
		if index == self.index:
			self.posCmdTarget = value
			self.uiCommandOutput.emit("COMMAND_MOVE", index, value)

	def getAxisTarget(self):
		try:
			return self._ui.sliderTarget.value()
		except Exception as err:
			return (int((2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1) / 2)
			print("getAxisTarget: " + str(err))

	def loadCenterUi(self,
			btnNudgeUp_in : qtw.QPushButton,
			btnNudgeDown_in : qtw.QPushButton):
		self._ui.loadCenterUi(btnNudgeUp_in, btnNudgeDown_in)
		self._ui.uiCenterNudge.connect(self.updateCenterNudge)

	def updateCenterNudge(self, index, direction):
		self.uiCommandOutput.emit("COMMAND_NUDGE_CENTER", index, direction)

	def loadEEPROMUi(self,
			btnSave_in: qtw.QPushButton,
			btnLoad_in: qtw.QPushButton,
			btnWipe_in: qtw.QPushButton):
		self._ui.loadEEPROMUi(btnSave_in, btnLoad_in, btnWipe_in)

	def loadEnableUi(self,
			btnEnable_in: qtw.QPushButton,
			labelEnable_in: qtw.QLabel):
		self._ui.loadEnableUi(btnEnable_in, labelEnable_in)
