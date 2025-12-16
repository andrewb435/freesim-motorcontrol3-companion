from PySide6.QtWidgets import QFrame, QSlider, QLabel, QPushButton, QDialog
from PySide6.QtCore import QObject, SignalInstance, Signal
from structure.AxisUi import AxisUi
from fsmc_settings import FSMC3Settings
from structure.AxisUiPIDInput import AxisUiPIDInput
from utils.Utils import Utils

class Axis(QObject):
	uiCommandOutput = Signal(str, int, int)

	def __init__(self, index):
		super().__init__()
		self.input				=	AxisUiPIDInput()
		self.index				=	index
		self._ui				=	AxisUi(index)
		self._communicator		=	None
		self.posSPI 		:	int	=	0
		self.posABZ 		:	int	=	0
		self.tunePIn		:	int	=	0
		self.tunePOut		:	int	=	0
		self.tuneIIn		:	int	=	0
		self.tuneIOut		:	int	=	0
		self.tuneDIn		:	int	=	0
		self.tuneDOut		:	int	=	0
		self.posCmdTarget	:	int	=	0
		self.posDevTarget	:	int	=	0
		self.enabled		:	int	=	0
		self.container		:	QFrame

	def loadAxisContainer(self, container : QFrame):
		self.container = container

	def checkAxisEnabled(self):
		if self.enabled > 0:
			self.container.setEnabled(True)
		else:
			self.container.setEnabled(False)

	def loadSPI(self,
			signal : SignalInstance,
			label : QLabel,
			slider : QSlider):
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
			label : QLabel,
			slider : QSlider):
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
			btnKp_in : QPushButton,
			btnKi_in : QPushButton,
			btnKd_in : QPushButton):
		signal.connect(self.updatePID)
		self._ui.loadPIDUi(btnKp_in, btnKi_in, btnKd_in)
		btnKp_in.clicked.connect(self.clickedKp)
		btnKi_in.clicked.connect(self.clickedKi)
		btnKd_in.clicked.connect(self.clickedKd)

	def updatePID(self, payload):
		tuneName = payload[self.index][0]
		tuneValue = payload[self.index][1]
		try:
			if tuneName == "p":
				truncVal = f"{tuneValue:.{3}f}"
				self._ui.updatePIDKp(truncVal)
				self.tunePIn = float(truncVal)
				if self.tunePOut == 0:
					self.tunePOut = self.tunePIn
			if tuneName == "i":
				truncVal = f"{tuneValue:.{4}f}"
				self._ui.updatePIDKi(truncVal)
				self.tuneIIn = float(truncVal)
				if self.tuneIOut == 0:
					self.tuneIOut = self.tuneIIn
			if tuneName == "d":
				truncVal = f"{tuneValue:.{4}f}"
				self._ui.updatePIDKd(truncVal)
				self.tuneDIn = float(truncVal)
				if self.tuneDOut == 0:
					self.tuneDOut = self.tuneDIn
		except Exception as err:
			print("updatePID: " + err)

	def clickedKp(self):
		self.input.feedSettings(
					FSMC3Settings.PID_KP_HI,
					self.tunePIn,
					FSMC3Settings.PID_KP_DECIMALS,
					.01)
		valKpFloat = self.getPIDinput()
		self.tunePOut = valKpFloat
		self.uiCommandOutput.emit("COMMAND_SET_P", self.index, int(valKpFloat))

	def getKp(self):
		val = Utils.mapRange(
			self.tunePOut,
			FSMC3Settings.PID_KPID_LO,
			FSMC3Settings.PID_KP_HI,
			FSMC3Settings.INT16_LO,
			FSMC3Settings.INT16_HI)
		return int(val)

	def clickedKi(self):
		self.input.feedSettings(
					FSMC3Settings.PID_KI_HI,
					self.tuneIIn,
					FSMC3Settings.PID_KID_DECIMALS,
					.001)
		valKiFloat = self.getPIDinput()
		self.tuneIOut = valKiFloat
		self.uiCommandOutput.emit("COMMAND_SET_I", self.index, int(valKiFloat))

	def getKi(self):
		val = Utils.mapRange(
			self.tuneIOut,
			FSMC3Settings.PID_KPID_LO,
			FSMC3Settings.PID_KI_HI,
			FSMC3Settings.INT16_LO,
			FSMC3Settings.INT16_HI)
		return int(val)

	def clickedKd(self):
		self.input.feedSettings(
					FSMC3Settings.PID_KD_HI,
					self.tuneDIn,
					FSMC3Settings.PID_KID_DECIMALS,
					.001)
		valKdFloat = self.getPIDinput()
		self.tuneDOut = valKdFloat
		self.uiCommandOutput.emit("COMMAND_SET_D", self.index, int(valKdFloat))

	def getKd(self):
		val = Utils.mapRange(
			self.tuneDOut,
			FSMC3Settings.PID_KPID_LO,
			FSMC3Settings.PID_KD_HI,
			FSMC3Settings.INT16_LO,
			FSMC3Settings.INT16_HI)
		return int(val)

	def getPIDinput(self):
		if self.input.spawnInput() == QDialog.Accepted:
			return self.input.ui.doubleSpinBox.value()

	def loadTarget(self,
			signal : Signal,
			label : QLabel,
			slider : QSlider,
			labelReported : QLabel,):
		self._ui.loadTargetUi(label, slider, labelReported)
		self._ui.uiTargetChange.connect(self.updateTargetFromUi)
		signal.connect(self._ui.updateTargetReportedUi)
	
	def updateTargetFromUi(self, index, value):
		if index == self.index:
			self.posCmdTarget = value
			self.uiCommandOutput.emit("COMMAND_MOVE", index, value)

	def getAxisTarget(self):
		try:
			return self.posCmdTarget
		except Exception:
			# return middle
			return (int((2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1) / 2)

	def loadCenterUi(self,
			btnNudgeUp_in : QPushButton,
			btnNudgeDown_in : QPushButton):
		self._ui.loadCenterUi(btnNudgeUp_in, btnNudgeDown_in)
		self._ui.uiCenterNudge.connect(self.updateCenterNudge)

	def updateCenterNudge(self, index, direction):
		self.uiCommandOutput.emit("COMMAND_NUDGE_CENTER", index, direction)

	def loadEEPROMUi(self,
			btnSave_in: QPushButton,
			btnLoad_in: QPushButton,
			btnWipe_in: QPushButton):
		self._ui.loadEEPROMUi(btnSave_in, btnLoad_in, btnWipe_in)

	def loadEnableUi(self,
			signal : Signal,
			btnEnable_in: QPushButton,
			labelEnable_in: QLabel):
		self._ui.loadEnableUi(btnEnable_in, labelEnable_in)
		self._ui.uiEnableClicked.connect(self.clickedEnableUi)
		signal.connect(self.updateEnabled)

	def updateEnabled(self, value):
		try:
			self.enabled = value[self.index]
			self._ui.updateEnabled(value)
			self.checkAxisEnabled()
		except Exception as err:
			print("updateEnabled: " + str(err))

	def clickedEnableUi(self):
		pass
