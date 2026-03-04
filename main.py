from PySide6 import QtWidgets as qtw
from PySide6.QtCore import QThread, QTimer

from ui.ui_main import Ui_qMain
from structure.FSMCData import FSMCData
from structure.FSMCGraph import FSMC3Grapher
from comm.comm_serial import SerialWorker
from parser.parser_fsmc3 import FSMC3Parser
from protocol.proto_fsmc3 import FSMC3Protocol

class AppUI(qtw.QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_qMain()
		self.ui.setupUi(self)
		self.parser = FSMC3Parser()
		self.grapher = FSMC3Grapher(self.ui.outputGraph)
		self.datamodel = FSMCData()
		self.datamodel.triggerCommand.connect(self.sendCommandToSerial)

		self._timer = QTimer()
		self._timer.timeout.connect(self._doPeriodic)
		self._timer.start(1000)
		
		self._serialThreading()
		self._comportList()
		self._connectMainUi()
		self._mapAxesUi_A()
		self._mapAxesUi_B()
		self._mapAxesUi_C()
		self._mapGraphUi()

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
		self.datamodel.loadEEPROMUi(
				self.ui.btnEEPROMSave_A,
				self.ui.btnEEPROMLoad_A,
				self.ui.btnEEPROMWipe_A,
			)

	def _mapAxesUi_A(self):
		# Axis A
		self.datamodel.AxisA.loadAxisContainer(
				self.ui.frmAxis_A
			)
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
				self.ui.btnKp_A,
				self.ui.btnKi_A,
				self.ui.btnKd_A
			)
		self.datamodel.AxisA.loadTarget(
				self.parser.axisTargetOut,
				self.ui.labelTarget_A,
				self.ui.sliderTarget_A,
				self.ui.labelTargetReported_A
			)
		self.datamodel.AxisA.loadCenterUi(
				self.ui.btnNudgeUp_A,
				self.ui.btnCenterSet_A,
				self.ui.btnNudgeDown_A
			)
		self.datamodel.AxisA.loadEnableUi(
				self.parser.axisEnOut,
				self.ui.btnEnable_A,
				self.ui.labelEnabled_A
			)
		
	def _mapAxesUi_B(self):
		# Axis B
		self.datamodel.AxisB.loadAxisContainer(
				self.ui.frmAxis_B
			)
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
				self.ui.btnKp_B,
				self.ui.btnKi_B,
				self.ui.btnKd_B
			)
		self.datamodel.AxisB.loadTarget(
				self.parser.axisTargetOut,
				self.ui.labelTarget_B,
				self.ui.sliderTarget_B,
				self.ui.labelTargetReported_B
			)
		self.datamodel.AxisB.loadCenterUi(
				self.ui.btnNudgeUp_B,
				self.ui.btnCenterSet_B,
				self.ui.btnNudgeDown_B
			)
		self.datamodel.AxisB.loadEnableUi(
				self.parser.axisEnOut,
				self.ui.btnEnable_B,
				self.ui.labelEnabled_B
			)

	def _mapAxesUi_C(self):
		# Axis C
		self.datamodel.AxisC.loadAxisContainer(
				self.ui.frmAxis_C
			)
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
				self.ui.btnKp_C,
				self.ui.btnKi_C,
				self.ui.btnKd_C
			)
		self.datamodel.AxisC.loadTarget(
				self.parser.axisTargetOut,
				self.ui.labelTarget_C,
				self.ui.sliderTarget_C,
				self.ui.labelTargetReported_C
			)
		self.datamodel.AxisC.loadCenterUi(
				self.ui.btnNudgeUp_C,
				self.ui.btnCenterSet_C,
				self.ui.btnNudgeDown_C
			)
		self.datamodel.AxisC.loadEnableUi(
				self.parser.axisEnOut,
				self.ui.btnEnable_C,
				self.ui.labelEnabled_C
			)

	def _mapGraphUi(self):
		self.grapher.loadGraphUi(
			self.parser.axisEnOut,
			self.parser.axisABZOut,
			self.datamodel.triggerCommand,
			self.ui.graphSelectA,
			self.ui.graphSelectB,
			self.ui.graphSelectC)

	def _doPeriodic(self):
		self.datamodel.periodicUpdate()

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
		self.ui.frmAxisControls.setEnabled(True)
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
		self.ui.frmAxisControls.setEnabled(False)
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