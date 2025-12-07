from PySide6 import QtWidgets as qtw
from PySide6.QtCore import QThread, Signal
from ui.ui_main import Ui_qMain
from structure.FSMCData import FSMCData
from comm.comm_serial import SerialWorker
from parser.parser_fsmc3 import FSMC3Parser
from protocol.proto_fsmc3 import FSMC3Protocol

class AppUI(qtw.QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_qMain()
		self.parser = FSMC3Parser()
		self.datamodel = FSMCData()
		self.datamodel.triggerCommand.connect(self.sendCommandToSerial)
		self.ui.setupUi(self)

		self._serialThreading()
		self._comportList()
		self._connectMainUi()
		self._mapAxesUi_A()
		self._mapAxesUi_B()
		self._mapAxesUi_C()

	def _serialThreading(self):
		self.serialThread = QThread()
		self.serialWorker = SerialWorker(self.parser.getCmd("COMMAND_REPORT"))
		self.serialWorker.data_received.connect(self.parser.sorter)
		self.serialWorker.moveToThread(self.serialThread)
		self.serialThread.started.connect(self.serialWorker.run)

	def _comportList(self):
		self.ui.boxComportList.clear()
		self.ui.boxComportList.addItems(self.serialWorker.getPortStrings())

	def _connectMainUi(self):
		self.ui.btnSerialConnect.clicked.connect(self.connectSerial)
		self.ui.btnSerialDisconnect.clicked.connect(self.disconnectSerial)
		self.ui.btnSerialRefresh.clicked.connect(self._comportList)

	def _mapAxesUi_A(self):
		# Axis A
		self.datamodel.AxisA.loadSPI(
				self.parser.axisSPIOut,
				self.ui.labelSPI_A,
				self.ui.sliderSPI_A
			)
		self.datamodel.AxisA.loadABZ(
				self.parser.axisABZOut,
				self.ui.labelABZ_A,
				self.ui.sliderABZ_A
			)
		self.datamodel.AxisA.loadPID(
				self.parser.axisPIDOut,
				self.ui.labelKp_A,
				self.ui.labelKi_A,
				self.ui.labelKd_A
			)
		self.datamodel.AxisA.loadTarget(
				self.parser.axisTargetOut,
				self.ui.labelTarget_A,
				self.ui.sliderTarget_A,
				self.ui.labelTargetReported_A
			)
		self.datamodel.AxisA.loadCenterUi(
				self.ui.btnNudgeUp_A,
				self.ui.btnNudgeDown_A
			)
		self.datamodel.AxisA.loadEnableUi(
				self.ui.btnEnable_A,
				self.ui.labelEnabled_A
			)
		
	def _mapAxesUi_B(self):
		# Axis B
		self.datamodel.AxisB.loadSPI(
				self.parser.axisSPIOut,
				self.ui.labelSPI_B,
				self.ui.sliderSPI_B
			)
		self.datamodel.AxisB.loadABZ(
				self.parser.axisABZOut,
				self.ui.labelABZ_B,
				self.ui.sliderABZ_B
			)
		self.datamodel.AxisB.loadPID(
				self.parser.axisPIDOut,
				self.ui.labelKp_B,
				self.ui.labelKi_B,
				self.ui.labelKd_B
			)
		self.datamodel.AxisB.loadTarget(
				self.parser.axisTargetOut,
				self.ui.labelTarget_B,
				self.ui.sliderTarget_B,
				self.ui.labelTargetReported_B
			)
		self.datamodel.AxisB.loadCenterUi(
				self.ui.btnNudgeUp_B,
				self.ui.btnNudgeDown_B
			)
		self.datamodel.AxisB.loadEnableUi(
				self.ui.btnEnable_B,
				self.ui.labelEnabled_B
			)

	def _mapAxesUi_C(self):
		# Axis C
		self.datamodel.AxisC.loadSPI(
				self.parser.axisSPIOut,
				self.ui.labelSPI_C,
				self.ui.sliderSPI_C
			)
		self.datamodel.AxisC.loadABZ(
				self.parser.axisABZOut,
				self.ui.labelABZ_C,
				self.ui.sliderABZ_C
			)
		self.datamodel.AxisC.loadPID(
				self.parser.axisPIDOut,
				self.ui.labelKp_C,
				self.ui.labelKi_C,
				self.ui.labelKd_C
			)
		self.datamodel.AxisC.loadTarget(
				self.parser.axisTargetOut,
				self.ui.labelTarget_C,
				self.ui.sliderTarget_C,
				self.ui.labelTargetReported_C
			)
		self.datamodel.AxisC.loadCenterUi(
				self.ui.btnNudgeUp_C,
				self.ui.btnNudgeDown_C
			)
		self.datamodel.AxisC.loadEnableUi(
				self.ui.btnEnable_C,
				self.ui.labelEnabled_C
			)

	def sendCommandToSerial(self, cmdType, cmdData):
		command = self.parser.getCmd(cmdType, cmdData)
		self.serialWorker.queueCommand(command)

	def connectSerial(self):
		if self.serialThread.isRunning():
			return
		else:
			self.serialWorker.setComport(self.ui.boxComportList.currentIndex())
			self.serialThread.start()
			self.connectSerialUi()

	def connectSerialUi(self):
		self.ui.frmAxis_A.setEnabled(True)
		self.ui.frmAxis_B.setEnabled(True)
		self.ui.frmAxis_C.setEnabled(True)
		self.ui.frmSystemEEPROM.setEnabled(True)
		self.ui.btnSerialDisconnect.setEnabled(True)
		self.ui.btnSerialConnect.setEnabled(False)
		self.ui.btnSerialRefresh.setEnabled(False)
		self.ui.labelConnected.setText("CONNECTED")

	def disconnectSerial(self):
		self.serialWorker.stop()
		self.serialThread.quit()
		self.serialThread.wait()
		self.disconnectSerialUi()

	def disconnectSerialUi(self):
		self.ui.frmAxis_A.setEnabled(False)
		self.ui.frmAxis_B.setEnabled(False)
		self.ui.frmAxis_C.setEnabled(False)
		self.ui.frmSystemEEPROM.setEnabled(False)
		self.ui.btnSerialDisconnect.setEnabled(False)
		self.ui.btnSerialConnect.setEnabled(True)
		self.ui.btnSerialRefresh.setEnabled(True)
		self.ui.labelConnected.setText("DISCONNECTED")
		self._comportList()

	def terminate_threads(self):
		try:
			self.serialWorker.stop()
			self.serialThread.quit()
			self.serialThread.wait()
		except Exception as err:
			print(err)