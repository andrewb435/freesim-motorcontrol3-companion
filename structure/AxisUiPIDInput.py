from PySide6.QtWidgets import QDialog
from ui.ui_input import Ui_Dialog as PIDInputDialog

class AxisUiPIDInput(QDialog):
	def __init__(self):
		super().__init__()
		self.ui = PIDInputDialog()
		self.ui.setupUi(self)

		self.tuneMin	=	0.0
		self.tuneMax	=	1.0
		self.curValue	=	0.0
		self.newValue	=	None

	def feedSettings(self, tuneMax_in, curVal_in, decimals_in, step_in):
		self.ui.doubleSpinBox.setMaximum(tuneMax_in)
		self.ui.doubleSpinBox.setValue(float(curVal_in))
		self.ui.doubleSpinBox.setDecimals(decimals_in)
		self.ui.doubleSpinBox.setSingleStep(step_in)
		self.ui.labelMax.setText(str(tuneMax_in))

	def spawnInput(self):
		return self.exec()
