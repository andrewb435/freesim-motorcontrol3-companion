import serial
from serial.tools.list_ports import comports as listComports
import time
import threading
from collections import deque
from utils.TickTimer import TickTimer
from PySide6.QtCore import Signal, QObject
from protocol.proto_fsmc3 import FSMC3Protocol
from utils.ascii_arduino import ard_ascii


class SerialDriver:
	def __init__(self):
		self.updateMs: int = 16	# 16ms = 62.5Hz updates
		self.port = None
		self.baud = 115200
		self.timer = TickTimer(self.updateMs)
		self.connection = None
		self.ready = True
		self.finder = SerialFinder()
		self.commandBuffer = deque()
		self.commandDefault = None
		self.bufferIndex = 0
		self.hasSync = False
		self._lockThread = threading.Lock()

	def selectSerial(self):
		self.port = self.finder.listPorts()
		if self.port is not None:
			self.initSerial()

	def setSerialPort(self, index_in):
		portName  = self.finder.portList[index_in]
		self.port = portName.device

	def closeSerial(self):
		try:
			self.connection.close(); # type: ignore
		except:
			print("Attempting to close failed, port not open")

	def initSerial(self):
		try:
			self.connection = serial.Serial(self.port, self.baud, timeout=1)
			print("Serial connected at " + str(self.port))
		except serial.SerialException as err:
			self.connection = None
			print("initSerial: " + str(err))

	def isReady(self) -> bool:
		if self.timer.check():
			self.ready = True
			return True
		else:
			return False

	def addCommandBuffer(self, command_in):
		self.commandBuffer.append(command_in)

	def getCommandBuffer(self):
		if len(self.commandBuffer) > 0 and self.ready:
			out = self.commandBuffer.popleft()
			return out
		else:
			return self.commandDefault
			return None

	def sendCommand(self):
		if self.isReady():
			command_in = self.getCommandBuffer()
			if command_in != None:
				self.ready = False
				try:
					if self.connection:
						if not self.connection.is_open:
							self.initSerial()
						if self.connection.is_open:
							try:
								bytes_written = self.connection.write(command_in)
								self.connection.flush()
							except Exception as err:
								self.connection.close()
								self.connection = None
								print("sendCommand: " + str(err))
					else:
						print('Retrying port ' + str(self.port) + ' at ' + str(self.baud) + ' baud')
						time.sleep(.25)
						self.initSerial()
				except:
					pass

	def receiveData(self):
		try:
			dataOut = None
			if self.connection:
				if self.connection.in_waiting >= FSMC3Protocol.MAXIMUM_LENGTH_BYTES:
					incoming : chr = self.connection.read(1)
					if incoming == FSMC3Protocol.COMMAND_OPEN.encode():
						incoming += (self.connection.read(FSMC3Protocol.MAXIMUM_LENGTH_BYTES - 1))
						if incoming[FSMC3Protocol.COMMAND_CLOSE_POSITION] == ard_ascii(FSMC3Protocol.COMMAND_CLOSE):
							self.hasSync = True
							dataOut = incoming
						else:
							self.hasSync = False
							dataOut = None
					if self.hasSync is True and dataOut is not None:
						try:
							return dataOut
						except Exception as err:
							print("rxdata inner " + str(err))
			else:
				print('Retrying port ' + str(self.port) + ' at ' + str(self.baud) + ' baud')
				time.sleep(.25)
				self.initSerial()
		except Exception as err:
			print("receiveData outer " + str(err))

class SerialWorker(QObject):
	data_received = Signal(bytes)
	def __init__(self, commandDefault_in : bytearray):
		super().__init__()
		self.comHandler = SerialDriver()
		self.comHandler.commandDefault = commandDefault_in
		self.running = True
		if self.comHandler.port is not None:
			self.comHandler.initSerial()

	def run(self):
		self.running = True
		while self.running:
			time.sleep(0.001)
			dataOut = self.comHandler.receiveData()
			if dataOut is not None:
				self.data_received.emit(dataOut)
			self.comHandler.sendCommand()

	def stop(self):
		self.running = False
		self.comHandler.closeSerial()

	def isRunning(self):
		return self.running
	
	def getPortStrings(self):
		return self.comHandler.finder.getPortStrings()

	def setComport(self, index):
		self.comHandler.setSerialPort(index)
		pass

	def queueCommand(self, command):
		self.comHandler.addCommandBuffer(command)

class Style:
	# Font effects
	BOLD = '\033[1m'
	ITALIC = '\033[3m'
	UNDERLINE = '\033[4m'
	# Font Colors
	RED = '\033[31m'
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	BLUE = '\033[34m'
	MAGENTA = '\033[35m'
	CYAN = '\033[36m'
	# END
	END = '\033[0m'

class SerialFinder:
	def __init__(self):
		self.portList = []
		self.portStrings = []
		self.portSelected = None
		self.targetVID = [
			0x2341,		# Arduino SA
			0x2A03,		# dog hunter AG (arduino)
			0x0483,		# STM
		]
		self.targetPID = [
			0x0001,		# dog hunter AG (Linino ONE bootloader) / Arduino SA (Uno CDC ACM)
			0x0043,		# dog hunter AG (Arduino Uno Rev3) / Arduino SA (Uno R3 CDC ACM)
			0x5740,		# Blackpill
		]

	def listPorts(self):
		self.portList = []
		ports = listComports()
		for port in sorted(ports):
			if port.description != 'n/a':
				self.portList.append(port)
		return
	
	def getPortStrings(self):
		self.listPorts()
		self.portStrings = []
		for port in self.portList:
			portstring = str(port.device) + " > " + str(port.description) + ", USB VID:PID=" + str(hex(port.vid)) + ":" + str(hex(port.pid))
			self.portStrings.append(portstring[:75])
		return self.portStrings
	
	# def selectPorts(self):
	# 	choice = ''
	# 	input_message = "Choose motion controller port:\n"
	# 	for index, port in enumerate(self.portList):
	# 		if port.vid in self.targetVID and port.pid in self.targetPID:
	# 			input_message += f'{Style.BOLD}{Style.YELLOW}{index + 1}) {"Port " + str(port.device) + " (Arduino Uno),Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}{Style.END}'
	# 		else:
	# 			input_message += f'{index + 1}) {"Port " + str(port.device) + ", Desc: " + str(port.description) + ", HWID: " + str(port.hwid) + "\n"}'
	# 	input_message += "Selection: "
	# 	while choice not in map(str, range(1, len(self.portList) + 1)):
	# 		choice = input(input_message)
	# 	print("Selected: " + str(self.portList[int(choice) - 1].device))
	# 	return self.portList[int(choice) - 1].device
