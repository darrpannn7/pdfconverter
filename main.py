from gui import WatermarkApp
from PyQt6.QtWidgets import QApplication
import sys
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec()) 