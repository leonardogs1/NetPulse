import os
import sys

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from services.network.monitor import NetworkMonitor
from ui.network_view import NetworkView

#from importlib.metadata import version # Gets value from pyproject.toml

from psutil import LINUX


def resolve_root():
    return os.path.dirname(os.path.abspath(__file__))

#---------------------------------------------------------------------------
#   GUI
#---------------------------------------------------------------------------
APP_TITLE = "NetPulse"
APP_SIZE = (800, 400)
APP_VERSION = "1.0.0"
APP_ICON = os.path.join(resolve_root(), "images", "Ubuntu-Style NT Heartbeat Icon.png")


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(APP_TITLE)
        self.resize(QSize(*APP_SIZE))
        self.setWindowIcon(QIcon(APP_ICON))

        # One tab per monitor. Add new ones here (e.g. Processes, Connections).
        self.tabs = QTabWidget()
        self.tabs.addTab(NetworkView(NetworkMonitor()), "Network")
        #self.tabs.addTab(CpuView(CpuMonitor()), "CPU")
        #self.tabs.addTab(ProcessView(ProcessMonitor()), "Process")
        #self.tabs.addTab(MemoryView(MemoryMonitor()), "Memory")
        #self.tabs.addTab(DisksView(DisksMonitor()), "Disks")
        #self.tabs.addTab(SensorsView(SensorMonitor()),"Sensor")
        self.setCentralWidget(self.tabs)

        self.statusBar().showMessage(f"{APP_TITLE} v{APP_VERSION}")


if __name__ == '__main__':
    if not LINUX:
        sys.exit("Error: 1.0.0 runs only on LINUX")
    
    #Create the Qt Application        
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
