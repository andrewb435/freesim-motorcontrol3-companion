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
		self.index	:	int		=	index
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
		self._ui.updateEnabled(self.enabled)

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
		slider.valueChanged.connect(self._pushTarget)
		signal.connect(self._updateTarget)
		self.posCmdTarget = slider.value()
	
	def updateTargetFromUi(self, index, value):
		if index == self.index:
			self.posCmdTarget = value
			self.uiCommandOutput.emit("COMMAND_MOVE", index, value)

	def getTarget(self):
		try:
			return self.posCmdTarget
		except Exception:
			# return middle
			return (int((2 ** FSMC3Settings.COMMAND_BIT_DEPTH) - 1) / 2)

	def _pushTarget(self, value):
		self.posCmdTarget = int(value)
		self._ui.pushTarget(str(self.posCmdTarget))
		self.uiCommandOutput.emit("COMMAND_MOVE", self.index, self.posCmdTarget)

	def _updateTarget(self, value):
		self.posDevTarget = value[self.index]
		self._ui.updateTarget(str(self.posDevTarget))

	def loadCenterUi(self,
			btnNudgeUp_in : QPushButton,
			btnCenterSet_in : QPushButton,
			btnNudgeDown_in : QPushButton):
		self._ui.loadCenterUi(btnNudgeUp_in, btnCenterSet_in, btnNudgeDown_in)
		btnNudgeUp_in.clicked.connect(self._pushCenterNudgeUp)
		btnCenterSet_in.clicked.connect(self._pushCenterSet)
		btnNudgeDown_in.clicked.connect(self._pushCenterNudgeDown)
	
	def _pushCenterNudgeUp(self):
		self.uiCommandOutput.emit("COMMAND_NUDGE_CENTER", self.index, 1)
		self._ui.centerTarget()

	def _pushCenterSet(self):
		self.uiCommandOutput.emit("COMMAND_SET_CENTER", self.index, 1)
		self._ui.centerTarget()

	def _pushCenterNudgeDown(self):
		self.uiCommandOutput.emit("COMMAND_NUDGE_CENTER", self.index, -1)
		self._ui.centerTarget()

	def loadEnableUi(self,
			signal : Signal,
			btnEnable_in: QPushButton,
			labelEnable_in: QLabel):
		self._ui.loadEnableUi(btnEnable_in, labelEnable_in)
		btnEnable_in.clicked.connect(self.clickedEnableUi)
		signal.connect(self.updateEnabled)

	def updateEnabled(self, value):
		self.enabled = value[self.index]
		self.checkAxisEnabled()

	def clickedEnableUi(self, index):
		if self.enabled <= 0:
			self.enabled = 1
		else:
			self.enabled = 0
		self.checkAxisEnabled()
		self.uiCommandOutput.emit("COMMAND_ENABLE", index, self.enabled)
	
	def getEnable(self):
		return self.enabled
