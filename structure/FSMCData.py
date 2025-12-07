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
		self.timer = TickTimer(20)	# 20ms = 50Hz updates
		self.moveDataFrame = [
			int(self.AxisA.getAxisTarget()),
			int(self.AxisB.getAxisTarget()),
			int(self.AxisC.getAxisTarget())]

	def getAxes(self) -> list[Axis]:
		return [self.AxisA, self.AxisB, self.AxisC]
	
	def buildCommand(self, cmdType, index, data):
		if cmdType == "COMMAND_MOVE":
			self.moveBuffer(index, data)
			pass
		else:
			dataOut = [0, 0, 0]
			dataOut[index] = int(data)
			self.triggerCommand.emit(cmdType, dataOut)
	
	def moveBuffer(self, index, data):
		self.moveDataFrame[index] = data
		if self.timer.check():
			self.triggerCommand.emit("COMMAND_MOVE", self.moveDataFrame)