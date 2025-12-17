from structure.Axis import Axis
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QObject, Signal
from utils.TickTimer import TickTimer

class FSMCData(QObject):
	triggerCommand		=	Signal(str, object)
	
	def __init__(self):
		super().__init__()
		self.AxisA	:	Axis	=	Axis(0)
		self.AxisB	:	Axis	=	Axis(1)
		self.AxisC	:	Axis	=	Axis(2)
		for axis in self.getAxes():
			axis.uiCommandOutput.connect(self.buildCommand)
		self.timer = TickTimer(10)	# 10ms = 100Hz updates for movement outputs
		self.moveDataFrame = [
			int(self.AxisA.getTarget()),
			int(self.AxisB.getTarget()),
			int(self.AxisC.getTarget())]
		self.packedDataFrame = [0,0,0]
		self.packerMethod = None
	
	def loadEEPROMUi(self,
			btnSave_in: QPushButton,
			btnLoad_in: QPushButton,
			btnWipe_in: QPushButton):
		btnSave_in.clicked.connect(self._pushEEPROMSaveToFlash)
		btnLoad_in.clicked.connect(self._pushEEPROMLoadFromFlash)
		btnWipe_in.clicked.connect(self._pushEEPROMWipeFlash)

	def _pushEEPROMSaveToFlash(self):
		self.buildCommand("COMMAND_EEPROM_SAVE", 0, 0)

	def _pushEEPROMLoadFromFlash(self):
		self.buildCommand("COMMAND_EEPROM_LOAD", 0, 0)

	def _pushEEPROMWipeFlash(self):
		self.buildCommand("COMMAND_EEPROM_WIPE", 0, 0)
	def getAxes(self) -> list[Axis]:
		return [self.AxisA, self.AxisB, self.AxisC]

	def periodicUpdate(self):
		dataOut = [0, 0, 0]
		self.triggerCommand.emit("COMMAND_STATIC", dataOut)

	def buildCommand(self, cmdType, index, data):
		if cmdType == "COMMAND_MOVE":
			self.packerMethod = Axis.getTarget
			self.packBuffer(cmdType)
		elif cmdType == "COMMAND_ENABLE":
			self.packerMethod = Axis.getEnable
			self.packBuffer(cmdType)
		elif cmdType == "COMMAND_SET_P":
			self.packerMethod = Axis.getKp
			self.packBuffer(cmdType)
		elif cmdType == "COMMAND_SET_I":
			self.packerMethod = Axis.getKi
			self.packBuffer(cmdType)
		elif cmdType == "COMMAND_SET_D":
			self.packerMethod = Axis.getKd
			self.packBuffer(cmdType)
		else:
			dataOut = [0, 0, 0]
			dataOut[index] = int(data)
			self.triggerCommand.emit(cmdType, dataOut)

	def packBuffer(self, cmdType):
		for index, axis in enumerate(self.getAxes()):
			self.packedDataFrame[index] = int(self.packerMethod(axis))

		# HACK: This is unsafe and could miss commands if the update rate is too slow
		if self.timer.check():
			self.triggerCommand.emit(cmdType, self.packedDataFrame)
