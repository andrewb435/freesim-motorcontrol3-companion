from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton
from PySide6.QtCore import Signal
import matplotlib
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from collections import deque

from fsmc_settings import FSMC3Settings
from protocol.proto_fsmc3 import FSMC3Protocol

matplotlib.use("qtagg")

class FSMC3Grapher(QWidget):
	def __init__(self, targetWidget):
		super().__init__()
		self.targetWidget = targetWidget
		self.dataTickHistoryLimit = 100 * 30 # 10ms ticks for 30 seconds (100 [times per second] * 30)
		self.currentAxis = 0	# Axis A = 0, B = 1, C = 2
		self.canvas = MplCanvas(self)
		self.uiSelects: QRadioButton = [None, None, None]
		self.configLayout()
		self.startGraph()

	def configLayout(self):
		"""
		Initialization routine to add a layout to the promoted widget, and add a matplotlib canvas to the layout
		"""
		layout = QVBoxLayout()
		layout.addWidget(self.canvas)
		layout.setContentsMargins(0,0,0,0)
		self.targetWidget.setLayout(layout)

	def loadGraphUi(self,
				 sigReturnedEnable: Signal,
				 sigReturnedPos: Signal,
				 sigCommandedPos: Signal,
				 uiSelectA: QRadioButton,
				 uiSelectB: QRadioButton,
				 uiSelectC: QRadioButton,
				 ):
		sigReturnedPos.connect(self.parseReturnedData)
		sigCommandedPos.connect(self.parseCommandedData)
		sigReturnedEnable.connect(self.sigEnabledFlags)
		self.uiSelects[0] = uiSelectA
		self.uiSelects[1] = uiSelectB
		self.uiSelects[2] = uiSelectC
		for radiobutton in self.uiSelects:
			radiobutton.clicked.connect(self.swapSelectedAxis)

	def parseReturnedData(self, data):
		self.canvas.addReturnedData(data[self.currentAxis])

	def parseCommandedData(self, commandType, data):
		if commandType == "COMMAND_MOVE":
			self.canvas.addCommandedData(data[self.currentAxis])
		if commandType == "COMMAND_ENABLE":
			self.sigEnabledFlags(data)

	def sigEnabledFlags(self, data):
		for i, radiobutton in enumerate(self.uiSelects):
			radiobutton.setEnabled(bool(data[i]))

	def swapSelectedAxis(self):
		if self.uiSelects[0].isChecked():
			self.currentAxis = 0
		if self.uiSelects[1].isChecked():
			self.currentAxis = 1
		if self.uiSelects[2].isChecked():
			self.currentAxis = 2

	def startGraph(self):
		self.canvas.startAnim()

	def stopGraph(self):
		self.canvas.stopAnim()

	def setAxisIndexToPlot(self, axisIndex):
		self.currentAxis = axisIndex

class MplCanvas(FigureCanvasQTAgg):
	def __init__(self, parent: FSMC3Grapher):
		self.figure = Figure()
		super().__init__(self.figure)
		self.ani = None
		# Graph colors
		# From https://www.nceas.ucsb.edu/sites/default/files/2022-06/Colorblind%20Safe%20Color%20Schemes.pdf
		self.colors = [
			'#f4b301', # R244 G179 B1
			'#db1048' # R219 G16 B72
		]
		self.posReturned = deque([0] * parent.dataTickHistoryLimit, maxlen=parent.dataTickHistoryLimit)
		self.posCommanded = deque([0] * parent.dataTickHistoryLimit, maxlen=parent.dataTickHistoryLimit)
		self.lastCommanded = pow(2,FSMC3Settings.COMMAND_BIT_DEPTH - 1)
		self.graphInterval = 1000/60	# 1000ms / 60 frames per second
		self.xData = range(parent.dataTickHistoryLimit)
		self.configFigure()
		self.axis = self.figure.add_subplot()
		self.configLines()
		self.configAxis()
	
	def configFigure(self):
		self.figure.tight_layout = True
		# self.figure.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
		self.figure.set_facecolor((0.25, 0.25, 0.25))

	"""
	Initialization
	"""
	def configLines(self):
		half = pow(2,FSMC3Settings.COMMAND_BIT_DEPTH - 1)
		self.lineMidline, = self.axis.plot(
			[0, len(self.xData)],
			[half, half],
			linewidth='1',
			color=(0.4, 0.4, 0.4, 0.5)
		)
		self.lineReturnedPos, = self.axis.plot(
			self.xData,
			self.posReturned,
			label="Reported",
			color=self.colors[0]
		)
		self.lineCommandedPos, = self.axis.plot(
			self.xData,
			self.posReturned,
			label="Commanded",
			color=self.colors[1]
		)

	def configAxis(self):
		self.axis.set_ylim(bottom=-1, top=pow(2,FSMC3Settings.COMMAND_BIT_DEPTH))
		self.axis.set_xlim(xmin=0, xmax=len(self.xData))
		self.axis.set_yticklabels([])
		self.axis.set_xticklabels([])
		self.axis.set_facecolor((0.25, 0.25, 0.25))
		self.axis.set_position([0,0,1,1])
		self.axis.legend(loc='upper left')

	def startAnim(self):
		if self.ani is None:
			self.ani = animation.FuncAnimation(
				self.figure,
				self.updateFrame,
				interval = self.graphInterval,
				blit=True,
				cache_frame_data=False
			)
		else:
			self.ani.event_source.start()

	def stopAnim(self):
		self.ani.event_source.stop()

	"""
	Methods
	"""
	def addReturnedData(self, data):
		self.posReturned.append(data)
		self.posCommanded.append(self.lastCommanded)

	def addCommandedData(self, data):
		if data > 0:
			self.lastCommanded = data

	def updateFrame(self, frame):
		self.lineReturnedPos.set_ydata(self.posReturned)
		self.lineCommandedPos.set_ydata(self.posCommanded)
		return self.lineReturnedPos, self.lineCommandedPos
