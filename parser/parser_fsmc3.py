from PySide6.QtCore import Signal, QObject
from protocol.proto_fsmc3 import FSMC3Protocol
from fsmc_settings import FSMC3Settings
from utils.ascii_arduino import ard_ascii
from utils.Utils import Utils

class FSMC3Parser(QObject):
	axisSPIOut = Signal(tuple)
	axisABZOut = Signal(tuple)
	axisTargetOut = Signal(tuple)
	axisPIDOut = Signal(tuple)
	axisEnOut = Signal(tuple)

	def __init__(self):
		super().__init__()
		self.buffer: chr = [None] * 3
		self.command = None

	def getCmd(self, cmdType, data = None):
		try:
			self.command = None
			cmdOut: chr = []
			if data == None:
				data = [0,0,0]
				if cmdType == None:
					return
			cmdOut.append(ard_ascii("["))
			cmdOut.append(ard_ascii(FSMC3Protocol.commands.get(cmdType)))
			byte_msb, byte_lsb = data[0].to_bytes(2, byteorder='big', signed=True)
			cmdOut.append(byte_msb)
			cmdOut.append(byte_lsb)
			byte_msb, byte_lsb = data[1].to_bytes(2, byteorder='big', signed=True)
			cmdOut.append(byte_msb)
			cmdOut.append(byte_lsb)
			byte_msb, byte_lsb = data[2].to_bytes(2, byteorder='big', signed=True)
			cmdOut.append(byte_msb)
			cmdOut.append(byte_lsb)
			cmdOut.append(ard_ascii("]"))
			self.command = bytearray(cmdOut)
			return self.command
		except Exception as err:
			print("getCmd: " + str(err))
			return

	def sorter(self, data : bytes):
		try:
			type = chr(list(data)[FSMC3Protocol.COMMAND_BYTE_POSITION])
		except:
			print(Exception)
		if type is FSMC3Protocol.responses.get("OUTPUT_SPI_POSITION"):
			self.parseSPI(data)
		elif type is FSMC3Protocol.responses.get("OUTPUT_ABZ_POSITION"):
			self.parseABZ(data)
		elif type is FSMC3Protocol.responses.get("OUTPUT_TARGET"):
			self.parseTarget(data)
		elif type is FSMC3Protocol.responses.get("OUTPUT_GET_P"):
			self.parseTuneP(data)
		elif type is FSMC3Protocol.responses.get("OUTPUT_GET_I"):
			self.parseTuneI(data)
		elif type is FSMC3Protocol.responses.get("OUTPUT_GET_D"):
			self.parseTuneD(data)
		elif type is FSMC3Protocol.responses.get("OUTPUT_GET_EN"):
			self.parseEnables(data)

	def parseCmd(self, buffer_in: bytes):
		try:
			self.buffer[0] = int.from_bytes(buffer_in[2:4], byteorder='big', signed=True)
			self.buffer[1] = int.from_bytes(buffer_in[4:6], byteorder='big', signed=True)
			self.buffer[2] = int.from_bytes(buffer_in[6:8], byteorder='big', signed=True)
			return self.buffer
		except Exception as err:
			print("parseCmd: " + str(err))
			return None
	
	def parseSPI(self, data):
		value = self.parseCmd(data)
		try:
			self.axisSPIOut.emit(
								(int(value[0]),
								int(value[1]),
								int(value[2]))
								)
		except Exception as err:
			print("parseSPI: " + str(err))

	def parseABZ(self, data):
		value = self.parseCmd(data)
		try:
			self.axisABZOut.emit(
								(int(value[0]),
								int(value[1]),
								int(value[2]))
								)
		except Exception as err:
			print("parseABZ: " + str(err))

	def parseTarget(self, data):
		value = self.parseCmd(data)
		try:
			self.axisTargetOut.emit(
								(int(value[0]),
								int(value[1]),
								int(value[2]))
								)
		except Exception as err:
			print("parseTarget: " + str(err))

	def parseTuneP(self, data):
		try:
			rawVals = self.parseCmd(data)
			mappedVals = [
				Utils.mapRange(
					value,
					FSMC3Settings.INT16_LO,
					FSMC3Settings.INT16_HI,
					FSMC3Settings.PID_KPID_LO,
					FSMC3Settings.PID_KP_HI)
				for value in rawVals
			]
			payload = (
				("p", float(mappedVals[0])),
				("p", float(mappedVals[1])),
				("p", float(mappedVals[2]))
				)
			self.axisPIDOut.emit(payload)
		except Exception as err:
			print("parseTuneP: " + str(err))

	def parseTuneI(self, data):
		try:
			rawVals = self.parseCmd(data)
			mappedVals = [
				Utils.mapRange(
					value,
					FSMC3Settings.INT16_LO,
					FSMC3Settings.INT16_HI,
					FSMC3Settings.PID_KPID_LO,
					FSMC3Settings.PID_KI_HI)
				for value in rawVals
			]
			payload = (
				("i", float(mappedVals[0])),
				("i", float(mappedVals[1])),
				("i", float(mappedVals[2]))
				)
			self.axisPIDOut.emit(payload)
		except Exception as err:
			print("parseTuneI: " + str(err))

	def parseTuneD(self, data):
		try:
			rawVals = self.parseCmd(data)
			mappedVals = [
				Utils.mapRange(
					value,
					FSMC3Settings.INT16_LO,
					FSMC3Settings.INT16_HI,
					FSMC3Settings.PID_KPID_LO,
					FSMC3Settings.PID_KD_HI)
				for value in rawVals
			]
			payload = (
				("d", float(mappedVals[0])),
				("d", float(mappedVals[1])),
				("d", float(mappedVals[2]))
				)
			self.axisPIDOut.emit(payload)
		except Exception as err:
			print("parseTuneD: " + str(err))
	
	def parseEnables(self, data):
		try:
			value = self.parseCmd(data)
			self.axisEnOut.emit(
					(int(value[0]),
					int(value[1]),
					int(value[2]))
					)
		except Exception as err:
			print("parseEnables: " + str(err))
