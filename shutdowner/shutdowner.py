import sys
import time
import subprocess
import ctypes
from res import str_abs_path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QRadioButton,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QToolTip,
)
from PyQt6.QtCore import QEvent, QTimer, QObject
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPoint

from localization import Str
from strict_int_validator import StrictIntValidator


STYLE_SHEET = """
    QLabel#TimeLeft {
        font: bold 35px 'Source Sans Pro';
        qproperty-alignment: AlignCenter;
    }
"""


def _showTip(widget, text_id):
    QToolTip.showText(
        widget.mapToGlobal(QPoint(0, 0)), Str.get(text_id), msecShowTime=2000)


class Shutdowner(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        self.setFixedSize(400, 140)
        self.setWindowTitle("Shutdowner")
        self.setWindowIcon(QIcon(str_abs_path("icons/shutdowner.ico")))

        self.setUpMainWindow()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTimeLeft)

        self.show()

    def setUpMainWindow(self):
        self.hours_edit = self._makeTimePartEdit("hh")
        self.minutes_edit = self._makeTimePartEdit("mm")
        self.seconds_edit = self._makeTimePartEdit("ss")

        hh_mm_delim = QLabel(":")
        mm_ss_delim = QLabel(":")

        time_h_box = QHBoxLayout()
        time_h_box.addWidget(self.hours_edit)
        time_h_box.addWidget(hh_mm_delim)
        time_h_box.addWidget(self.minutes_edit)
        time_h_box.addWidget(mm_ss_delim)
        time_h_box.addWidget(self.seconds_edit)

        self.time_input_container = QFrame()
        self.time_input_container.setLayout(time_h_box)

        self.time_left_label = QLabel()
        self.time_left_label.setObjectName("TimeLeft")

        self.time_layout = QStackedLayout()
        self.time_layout.addWidget(self.time_input_container)
        self.time_layout.addWidget(self.time_left_label)

        #
        self.power_off_rb = self._makeModeRadioButton("Power off")
        self.hibernate_rb = self._makeModeRadioButton("Hibernate")
        self.restart_rb = self._makeModeRadioButton("Restart")

        self.hibernate_rb.setChecked(True)

        self.run_button = QPushButton()
        self.run_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.run_button.clicked.connect(self.run)

        buttons_v_box = QVBoxLayout()
        buttons_v_box.addWidget(self.power_off_rb)
        buttons_v_box.addWidget(self.hibernate_rb)
        buttons_v_box.addWidget(self.restart_rb)
        buttons_v_box.addWidget(self.run_button)

        buttons_container = QFrame()
        buttons_container.setLayout(buttons_v_box)

        #
        h_box = QHBoxLayout()
        h_box.addLayout(self.time_layout)
        h_box.addWidget(buttons_container)

        self.setLayout(h_box)

        #
        self._prepareStart()

    def updateTimeLeft(self):
        seconds_to_shutdown = round(self.finish_time - time.time())

        if seconds_to_shutdown > 0:
            d = (seconds_to_shutdown // 3600) // 24
            h = (seconds_to_shutdown // 3600) % 24
            m = (seconds_to_shutdown % 3600) // 60
            s = seconds_to_shutdown % 60

            #
            time_left = f"{d} day(s) " if d > 0 else ""
            time_left += f"{h:02}:{m:02}:{s:02}"

            self.time_left_label.setText(time_left)

        else:
            self.run()  # stop counting

            if self.power_off_rb.isChecked():
                shutdown_arg = "/s"
            if self.hibernate_rb.isChecked():
                shutdown_arg = "/h"
            if self.restart_rb.isChecked():
                shutdown_arg = "/r"

            subprocess.call(["shutdown", shutdown_arg])

    def run(self):
        if not self.timer.isActive():
            h = self._strToInt(self.hours_edit.text())
            m = self._strToInt(self.minutes_edit.text())
            s = self._strToInt(self.seconds_edit.text())

            time_left_s = h * 3600 + m * 60 + s
            if time_left_s == 0:
                _showTip(self.run_button, "Enter time!")
                return

            #
            self.finish_time = time.time() + time_left_s

            self.timer.start(1000)
            self._prepareStop()

        else:
            self.timer.stop()
            self._prepareStart()

    def togglePowerOff(self):
        self.power_off_rb.toggle()

    def toggleHibernate(self):
        self.hibernate_rb.toggle()

    def toggleRestart(self):
        self.restart_rb.toggle()

    def _makeTimePartEdit(self, placeholder_text_id):
        edit = QLineEdit()
        edit.setPlaceholderText(Str.get(placeholder_text_id))
        edit.setValidator(
            StrictIntValidator(lambda text_id: _showTip(edit, text_id)))
        edit.setObjectName("TimePartEdit")
        return edit

    def _makeModeRadioButton(self, text_id):
        rb = QRadioButton(Str.get(text_id))
        rb.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        rb.setObjectName("Mode")
        return rb

    def _prepareStart(self):
        self.run_button.setText(Str.get("Start"))

        self.time_layout.setCurrentWidget(self.time_input_container)

        self.hours_edit.clear()
        self.minutes_edit.clear()
        self.seconds_edit.clear()

        self.hours_edit.setFocus()

    def _prepareStop(self):
        self.run_button.setText(Str.get("Stop"))

        self.time_layout.setCurrentWidget(self.time_left_label)

        self.updateTimeLeft()

    def _strToInt(self, text):
        try:
            return int(text)
        except ValueError:
            return 0


class ShortcutsCatcher(QObject):
    def __init__(self, main_wnd):
        super().__init__()

        self.shortcuts = [
            {
                "keys":
                    [Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_S, 1067, 1030],
                "trig": main_wnd.run,
            },
            {
                "keys": [Qt.Key.Key_P, 1047],
                "trig": main_wnd.togglePowerOff,
            },
            {
                "keys": [Qt.Key.Key_H, 1056],
                "trig": main_wnd.toggleHibernate,
            },
            {
                "keys": [Qt.Key.Key_R, 1050],
                "trig": main_wnd.toggleRestart,
            },
            {
                "keys": [Qt.Key.Key_Escape],
                "trig": main_wnd.close,
            }
        ]

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            for shortcut in self.shortcuts:
                if event.key() in shortcut["keys"]:
                    shortcut["trig"]()
                    return True
        return False


if __name__ == "__main__":
    myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    window = Shutdowner()

    shortcuts_catcher = ShortcutsCatcher(window)
    app.installEventFilter(shortcuts_catcher)
    app.setStyleSheet(STYLE_SHEET)

    sys.exit(app.exec())
