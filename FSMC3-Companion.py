from PySide6 import QtWidgets as qtw
from main import AppUI

if __name__ == "__main__":
	app = qtw.QApplication([])
	appui = AppUI()
	appui.show()
	app.aboutToQuit.connect(appui.terminate_threads)
	app.exec()