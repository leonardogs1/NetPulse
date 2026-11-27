from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utils import format_bytes

REFRESH_MS = 1000
COLUMNS = ["Interface", "Status", "IPv4", "Send", "Receive", "Total sent", 
           "Total received", "Total err/drops"]


class NetworkView(QWidget):
    """Live table of network interfaces, refreshed every REFRESH_MS."""

    def __init__(self, monitor, parent=None):
        super().__init__(parent)
        self.monitor = monitor

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(REFRESH_MS)
        self.refresh()

    def refresh(self):
        interfaces = self.monitor.collect_all()
        self.table.setRowCount(len(interfaces))

        for row, iface in enumerate(interfaces):
            print(row, iface)
            values = [
                iface.name,
                "Up" if iface.is_up else "Down",
                iface.ipv4 or "-",
                f"{format_bytes(iface.send_rate)}/s",
                f"{format_bytes(iface.recv_rate)}/s",
                format_bytes(iface.bytes_sent),
                format_bytes(iface.bytes_recv),
                f"{iface.errin + iface.errout + iface.dropin + iface.dropout}"
            ]
            print(f"values: {values}")
            for col, value in enumerate(values):
                self._set_cell(row, col, value)

    def _set_cell(self, row, col, text):
        # Reuse existing items so the selection doesn't reset every refresh.
        item = self.table.item(row, col)
        if item is None:
            self.table.setItem(row, col, QTableWidgetItem(text))
        else:
            item.setText(text)
