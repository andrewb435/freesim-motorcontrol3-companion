from structure.Axis import Axis
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
			int(self.AxisA.getAxisTarget()),
			int(self.AxisB.getAxisTarget()),
			int(self.AxisC.getAxisTarget())]
		self.packedDataFrame = [0,0,0]

	def getAxes(self) -> list[Axis]:
		return [self.AxisA, self.AxisB, self.AxisC]

	def periodicUpdate(self):
		dataOut = [0, 0, 0]
		self.triggerCommand.emit("COMMAND_STATIC", dataOut)

	def buildCommand(self, cmdType, index, data):
		if cmdType == "COMMAND_MOVE":
			self.moveBuffer(index, data)
		elif cmdType == "COMMAND_SET_P":
			self.packKp()
		elif cmdType == "COMMAND_SET_I":
			self.packI()
		elif cmdType == "COMMAND_SET_D":
			self.packD()
		else:
			dataOut = [0, 0, 0]
			dataOut[index] = int(data)
			self.triggerCommand.emit(cmdType, dataOut)
	
	def moveBuffer(self, index, data):
		self.moveDataFrame[index] = data
		if index != 0:
			self.moveDataFrame[0] = self.AxisA.getAxisTarget()
		if index != 1:
			self.moveDataFrame[1] = self.AxisB.getAxisTarget()
		if index != 2:
			self.moveDataFrame[2] = self.AxisC.getAxisTarget()
		if self.timer.check():
			self.triggerCommand.emit("COMMAND_MOVE", self.moveDataFrame)

	def packKp(self):
		for index, axis in enumerate(self.getAxes()):
			self.packedDataFrame[index] = int(axis.getKp())
		self.triggerCommand.emit("COMMAND_SET_P", self.packedDataFrame)

	def packI(self):
		for index, axis in enumerate(self.getAxes()):
			self.packedDataFrame[index] = int(axis.getKi())
		self.triggerCommand.emit("COMMAND_SET_I", self.packedDataFrame)

	def packD(self):
		for index, axis in enumerate(self.getAxes()):
			self.packedDataFrame[index] = int(axis.getKd())
		self.triggerCommand.emit("COMMAND_SET_D", self.packedDataFrame)
