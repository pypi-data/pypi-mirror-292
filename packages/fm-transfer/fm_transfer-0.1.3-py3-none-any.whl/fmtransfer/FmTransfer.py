import os
import re
import tempfile
from pathlib import Path
from typing import Any, Optional

import serial.serialutil
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6.QtSerialPort import QSerialPortInfo
from PyQt6 import QtCore
from serial import Serial
from .FmWindow import Ui_FmTransfer


class FmTransfer(QMainWindow, Ui_FmTransfer):

    def __init__(self, **kwargs: Any) -> None:
        super(FmTransfer, self).__init__(**kwargs)
        self._tool = True
        self._quiet_protocol_list = ["audible", "audible-7k-channel-0", "audible-7k-channel-1",
                                     "cable-64k", "ultrasonic",
                                     "ultrasonic-3600", "ultrasonic-whisper"]
        self._quiet_protocol = 0
        self._gg_protocol = 2
        self.setupUi(FmTransfer=self)  # type: ignore[no-untyped-call]
        self._serialdevice: Optional[Serial] = None
        self._serial = ""
        self._serial_index = 0
        self._serial_closed = True
        self._com_ports = ["none"]
        self.recheck_serial_ports()
        self.pttPressedRadioButton.toggled['bool'].connect(self.led.setOn)
        self.pttGroupBox.setDisabled(True)
        self.signalGroupBox.setDisabled(True)
        self.checkSignalButton.setDisabled(True)
        self.led.setDisabled(True)
        self._ptt_unpressed: bool = True
        self._signal_dtr = True  # DSR, True = RTS
        self._send_filename: Optional[str] = None
        self._receive_filename: Optional[str] = None
        self._ggtransfer = True
        self._process_send = QtCore.QProcess(self)
        self._process_send.readyRead.connect(self._send_data_ready)
        self._process_send.started.connect(self._send_data_started)
        self._process_send.finished.connect(self._send_data_end)
        self._process_send_msg = QtCore.QProcess(self)
        self._process_send_msg.readyRead.connect(self._send_msg_data_ready)
        self._process_send_msg.started.connect(self._send_msg_data_started)
        self._process_send_msg.finished.connect(self._send_msg_data_end)
        self._process_receive = QtCore.QProcess(self)
        self._process_receive.readyRead.connect(self._receive_data_ready)
        self._process_receive.started.connect(self._receive_data_started)
        self._process_receive.finished.connect(self._receive_data_end)
        self._process_receive_msg = QtCore.QProcess(self)
        self._process_receive_msg.readyRead.connect(self._receive_msg_data_ready)
        self._process_receive_msg.started.connect(self._receive_msg_data_started)
        self._process_receive_msg.finished.connect(self._receive_msg_data_end)
        self._receive_in_progress = False
        self._send_in_progress = False
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self._pieces = 1
        self._current_piece = 0
        self._protocol = 0
        self._crc32 = ""
        self._tempfile: Optional[int] = None
        self._tempfilename: Optional[str] = None
        self._load_settings()

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore[override]
        # settings = QSettings(r"r:\settings.ini", QSettings.Format.IniFormat)
        settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "fm-transfer",
                             "fm-transfer")
        settings.setValue("MainWindow/geometry", self.saveGeometry())
        settings.setValue("MainWindow/state", self.saveState())
        if self._receive_filename is not None:
            settings.setValue("MainWindow/receivefile", self._receive_filename)
        if self._send_filename is not None:
            settings.setValue("MainWindow/sendfile", self._send_filename)
        settings.setValue("MainWindow/tool", self._tool)
        settings.setValue("MainWindow/quiet_protocol", self._quiet_protocol)
        settings.setValue("MainWindow/gg_protocol", self._gg_protocol)
        settings.setValue("MainWindow/signal", self._signal_dtr)
        settings.setValue("MainWindow/serial", self._serial)
        settings.setValue("MainWindow/serial_index", self._serial_index)
        super().closeEvent(event)

    def _load_settings(self) -> None:
        # settings = QSettings(r"r:\settings.ini", QSettings.Format.IniFormat)
        settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "fm-transfer",
                             "fm-transfer")
        self.restoreGeometry(settings.value("MainWindow/geometry", self.saveGeometry()))
        self.restoreState(settings.value("MainWindow/state", self.saveState()))
        send_filename = settings.value("MainWindow/sendfile", None)
        if send_filename is not None:
            self._send_filename = send_filename
            assert self._send_filename is not None
            short_fname = ('...' + self._send_filename[-20:]) if len(
                self._send_filename) > 20 else self._send_filename
            self.sendFileLineEdit.setText(short_fname)
        receive_filename = settings.value("MainWindow/receivefile", None)
        if receive_filename is not None:
            self._receive_filename = receive_filename
            assert self._receive_filename is not None
            short_fname = ('...' + self._receive_filename[-20:]) if len(
                self._receive_filename) > 20 else self._receive_filename
            self.receiveFileLineEdit.setText(short_fname)

        self._tool = settings.value("MainWindow/tool", self._tool, bool)
        self.quietRadioButton.setChecked(not self._tool)
        if self._tool:
            self.set_tool(self._tool)

        gg_protocol = settings.value("MainWindow/gg_protocol", self._gg_protocol, int)
        self.ggProtocolComboBox.setCurrentIndex(gg_protocol)
        quiet_protocol = settings.value("MainWindow/quiet_protocol", self._quiet_protocol, int)
        self.quietProtocolComboBox.setCurrentIndex(quiet_protocol)

        signal = settings.value("MainWindow/signal", self._signal_dtr, bool)
        self._signal_dtr = signal
        self.rtsRadioButton.setChecked(not self._signal_dtr)

        serial_name = settings.value("MainWindow/serial", "")
        serial_index = settings.value("MainWindow/serial_index", self._serial_index, int)
        if serial_index < len(self._com_ports):
            if self._com_ports[serial_index] == serial_name:
                self.serialComboBox.setCurrentIndex(serial_index)

    def _disable_interface_elements(self, mode: str) -> None:

        self.checkSignalButton.setDisabled(True)

        self.led.setDisabled(True)

        self.protocolGroupBox.setDisabled(True)
        self.pttGroupBox.setDisabled(True)
        self.signalGroupBox.setDisabled(True)
        self.toolGroupBox.setDisabled(True)

        self.serialComboBox.setDisabled(True)

        self.shortMsg.setDisabled(True)

        self.chooseSendFileButton.setDisabled(True)
        self.chooseRecvFileButton.setDisabled(True)

        if mode == "send_file":
            self.sendFileButton.setText("Stop sending")
            self.receiveButton.setDisabled(True)
            self.sendMsgButton.setDisabled(True)
            self.recvMsgButton.setDisabled(True)
        elif mode == "receive_file":
            self.sendFileButton.setDisabled(True)
            self.receiveButton.setText("Stop receiving")
            self.sendMsgButton.setDisabled(True)
            self.recvMsgButton.setDisabled(True)
        elif mode == "send_msg":
            self.sendFileButton.setDisabled(True)
            self.receiveButton.setDisabled(True)
            # self.sendMsgButton.setDisabled(True)
            self.sendMsgButton.setText("Sending...")
            self.recvMsgButton.setDisabled(True)
        elif mode == "receive_msg":
            self.sendFileButton.setDisabled(True)
            self.receiveButton.setDisabled(True)
            self.sendMsgButton.setDisabled(True)
            self.recvMsgButton.setText("Receiving...")
            # self.recvMsgButton.setDisabled(True)
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def _enable_interface_elements(self) -> None:

        self.checkSignalButton.setDisabled(self._serial_closed)

        self.led.setDisabled(self._serial_closed)

        self.protocolGroupBox.setDisabled(False)
        self.pttGroupBox.setDisabled(self._serial_closed)
        self.signalGroupBox.setDisabled(self._serial_closed)
        self.toolGroupBox.setDisabled(False)

        self.serialComboBox.setDisabled(False)

        self.shortMsg.setDisabled(False)

        self.chooseSendFileButton.setDisabled(False)
        self.chooseRecvFileButton.setDisabled(False)

        _trans = QtCore.QCoreApplication.translate
        self.sendFileButton.setText(_trans("FmTransfer", "Send file"))
        self.receiveButton.setText(_trans("FmTransfer", "Receive file"))
        self.recvMsgButton.setText(_trans("FmTransfer", "Receive"))
        self.sendMsgButton.setText(_trans("FmTransfer", "Send"))

        self.sendFileButton.setDisabled(False)
        self.receiveButton.setDisabled(False)
        self.sendMsgButton.setDisabled(False)
        self.recvMsgButton.setDisabled(False)

    def _send_msg_data_ready(self) -> None:
        new = str(self._process_send_msg.readAll().data(), 'utf-8')
        # new = re.sub(r"\r", "\n", new)
        for line in new.splitlines():
            if line.startswith("Piece "):
                match = re.match(r"Piece (\d+)/(\d+)", line)
                if match is not None:
                    self._current_piece = int(match.group(1))
                    self._pieces = int(match.group(2))
                    self.progressBar.setMaximum(self._pieces)
                    self.progressBar.setValue(self._current_piece)
            elif line.startswith("Speed"):
                self.messages.insertPlainText(line + "\n")
                self.messages.ensureCursorVisible()

    def _send_msg_data_started(self) -> None:
        self._pieces = 1
        self._current_piece = 0
        self.progressBar.setMaximum(self._pieces)
        self.progressBar.setValue(self._current_piece)
        self._disable_interface_elements("send_msg")

    def _send_msg_data_end(self) -> None:
        if self._tempfilename is not None:
            os.unlink(self._tempfilename)
            self._tempfilename = None
        self._send_in_progress = False
        if not self._serial_closed:
            self.pttReleasedRadioButton.setChecked(True)
        self._enable_interface_elements()

    def _receive_msg_data_ready(self) -> None:
        new = str(self._process_send_msg.readAll().data(), 'utf-8')
        # new = re.sub(r"\r", "\n", new)
        for line in new.splitlines():
            self.messages.insertPlainText(line + "\n")
            self.messages.ensureCursorVisible()

    def _receive_msg_data_started(self) -> None:
        self._pieces = 1
        self._current_piece = 0
        self.progressBar.setMaximum(self._pieces)
        self.progressBar.setValue(self._current_piece)
        self._disable_interface_elements("receive_msg")

    def _receive_msg_data_end(self) -> None:
        if self._tempfilename is not None:
            if os.path.isfile(self._tempfilename):
                with open(self._tempfilename, "rb") as f:
                    self._current_piece = 1
                    self.progressBar.setValue(self._current_piece)
                    self.messages.insertPlainText(f.read().decode("utf-8") + "\n")
                    self.messages.ensureCursorVisible()
                os.unlink(self._tempfilename)
            self._tempfilename = None
        self._receive_in_progress = False
        self._enable_interface_elements()

    def _send_data_ready(self) -> None:
        new = str(self._process_send.readAll().data(), 'utf-8')
        # new = re.sub(r"\r", "\n", new)
        for line in new.splitlines():
            if line.startswith("Pieces: "):
                match = re.match(r"Pieces: (\d+)", line)
                if match is not None:
                    self._pieces = int(match.group(1))
                    self.progressBar.setMaximum(self._pieces)
                    self.messages.insertPlainText(line + "\n")
            elif line.startswith("Piece "):
                match = re.match(r"Piece (\d+)", line)
                if match is not None:
                    self._current_piece = int(match.group(1))
                    self.progressBar.setValue(self._current_piece)
            elif line.startswith("Speed") or line.startswith("Sending") or line.startswith("Time"):
                self.messages.insertPlainText(line + "\n")
            elif line.startswith("Size:"):
                match = re.match(r"Size: (\d+)", line)
                if match is not None:
                    self._pieces = int(match.group(1))
                    self.progressBar.setMaximum(self._pieces)
                    self.messages.insertPlainText(line + "\n")
            elif line.startswith("Sent:"):
                match = re.match(r"Sent: (\d+)", line)
                if match is not None:
                    self._current_piece = int(match.group(1))
                    self.progressBar.setValue(self._current_piece)
        self.messages.ensureCursorVisible()

    def _send_data_started(self) -> None:
        self._pieces = 1
        self._current_piece = 0
        self.progressBar.setMaximum(self._pieces)
        self.progressBar.setValue(self._current_piece)
        self._disable_interface_elements("send_file")

    def _send_data_end(self) -> None:
        self._send_in_progress = False
        self._enable_interface_elements()
        if not self._serial_closed:
            self.pttReleasedRadioButton.setChecked(True)

    def _receive_data_ready(self) -> None:
        new = str(self._process_receive.readAll().data(), 'utf-8')
        # new = re.sub(r"\r", "\n", new)
        for line in new.splitlines():
            if line.startswith("Got header"):
                match = re.match(r".*pieces: (\d+)", line)
                if match is not None:
                    self._pieces = int(match.group(1))
                    self.progressBar.setMaximum(self._pieces)
                    self.messages.insertPlainText(f"Got pieces number: {self._pieces}" + "\n")
                match = re.match(r".*CRC32: (.{8}).*", line)
                if match is not None:
                    self._crc32 = match.group(1)
                    self.messages.insertPlainText(f"Got CRC: {self._crc32}" + "\n")
                self.messages.insertPlainText(line + "\n")
            elif line.startswith("Piece "):
                match = re.match(r"Piece (\d+)", line)
                if match is not None:
                    self._current_piece = int(match.group(1))
                    self.progressBar.setValue(self._current_piece)
            elif line.startswith("Speed") or line.find("ERROR") != -1:
                self.messages.insertPlainText(line + "\n")
            elif line.startswith("Size:"):
                match = re.match(r"Size: (\d+)", line)
                if match is not None:
                    self._pieces = int(match.group(1))
                    self.progressBar.setMaximum(self._pieces)
                    self.messages.insertPlainText(line + "\n")
            elif line.startswith("Received:"):
                match = re.match(r"Received: (\d+)", line)
                if match is not None:
                    self._current_piece = int(match.group(1))
                    self.progressBar.setValue(self._current_piece)
            elif line.startswith("Time") or line.startswith("Speed") or line.startswith("CRC"):
                self.messages.insertPlainText(line + "\n")

        self.messages.ensureCursorVisible()

    def _receive_data_started(self) -> None:
        self._pieces = 1
        self._current_piece = 0
        self.progressBar.setMaximum(self._pieces)
        self.progressBar.setValue(self._current_piece)
        self._disable_interface_elements("receive_file")

    def _receive_data_end(self) -> None:
        self._enable_interface_elements()
        self._receive_in_progress = False
        # if self.pttGroupBox.isEnabled()
        # if not self._serial_closed:
        #     self.pttReleasedRadioButton.setChecked(True)

    # noinspection PyUnresolvedReferences
    def reinit_serial(self, index: int) -> None:
        self._serial_index = index
        if self._serialdevice and self._serialdevice.is_open:
            self._serialdevice.close()
            self._serialdevice = None
            self._serial_closed = True
        if self._serial_index == 0:
            self._serialdevice = None
            self.pttGroupBox.setDisabled(True)
            self.signalGroupBox.setDisabled(True)
            self.checkSignalButton.setDisabled(True)
            self._serial_closed = True
            self.led.setDisabled(True)
        else:
            self._serial = self._com_ports[self._serial_index]
            self._serialdevice = Serial(baudrate=9600)
            self._serialdevice.dtr = True
            self._serialdevice.rts = True
            self._serialdevice.port = self._serial
            try:
                self._serial_closed = not self._serialdevice.is_open
                if self._serial_closed:
                    self._serialdevice.open()
                    self._serial_closed = False
                    self.pttGroupBox.setDisabled(False)
                    self.signalGroupBox.setDisabled(False)
                    self.led.setDisabled(False)
                    self.checkSignalButton.setDisabled(False)
                    self._send_signal()
                    self.check_signal()
            except serial.serialutil.SerialException as e:
                self.messages.insertPlainText(str(e) + "\n")
                self.messages.ensureCursorVisible()
                self.serialComboBox.setCurrentIndex(0)
            except Exception as e:
                self.messages.insertPlainText(str(e) + "\n")
                self.messages.ensureCursorVisible()
                self.serialComboBox.setCurrentIndex(0)

    # noinspection PyUnresolvedReferences
    def _send_signal(self) -> None:
        if self._serialdevice and self._serialdevice.is_open:
            # print("ptt", self._ptt_unpressed)
            if self._ptt_unpressed:
                self._serialdevice.dtr = True
                self._serialdevice.rts = True
            else:
                # print("signal", self._signal_dtr)
                if self._signal_dtr:
                    self._serialdevice.dtr = False
                    self._serialdevice.rts = True
                else:
                    self._serialdevice.dtr = True
                    self._serialdevice.rts = False

    def check_signal(self) -> None:
        # noinspection PyUnresolvedReferences
        if self._serialdevice and self._serialdevice.is_open:
            if self._serialdevice.dtr:
                self.messages.insertPlainText("DTR signal DOWN\n")
            else:
                self.messages.insertPlainText("DTR signal UP\n")
            if self._serialdevice.rts:
                self.messages.insertPlainText("RTS signal DOWN\n")
            else:
                self.messages.insertPlainText("RTS signal UP\n")
        self.messages.ensureCursorVisible()

    def toggle_ptt(self, checked: bool) -> None:
        # noinspection PyUnresolvedReferences
        if not self._serial_closed:
            self._ptt_unpressed = checked
            self._send_signal()
            self.check_signal()

    def toggle_signal(self, signal: bool) -> None:
        # noinspection PyUnresolvedReferences
        if not self._serial_closed:
            self._signal_dtr = signal
            self._send_signal()
            self.check_signal()

    def recheck_serial_ports(self) -> None:

        if not self._serial_closed and isinstance(self._serialdevice, Serial):
            self.pttReleasedRadioButton.setChecked(True)
            self._serialdevice.close()
            self._serial_closed = True
            self._serial = ""
            self._serialdevice = None
        try:
            self.serialComboBox.currentIndexChanged.disconnect(self.reinit_serial)
        except TypeError:
            pass
        self.serialComboBox.clear()
        self._com_ports = ["none"]
        self.serialComboBox.addItem("Choose a serial port...")
        available_ports = QSerialPortInfo.availablePorts()
        for port in available_ports:
            self._com_ports.append(port.systemLocation())
            self.serialComboBox.addItem(port.systemLocation())
        self.serialComboBox.currentIndexChanged.connect(self.reinit_serial)

    def send_file(self) -> None:
        if not self._send_in_progress:
            if not self._send_filename or not Path(self._send_filename).is_file():
                self.choose_send_file()
            if self._send_filename is not None and Path(self._send_filename).is_file():
                if not self._serial_closed and self.pttGroupBox.isEnabled():
                    self.pttPressedRadioButton.setChecked(True)
                if self._tool:
                    ex = "gg-transfer"
                    argss = f"send -p {self._gg_protocol} -f -i".split(" ")
                    # noinspection PyTypeChecker
                    argss.append(self._send_filename)
                else:
                    ex = "quiet-transfer"
                    argss = f"send -p {self._quiet_protocol_list[self._quiet_protocol]} -f -i".split(" ")
                    # noinspection PyTypeChecker
                    argss.append(self._send_filename)
                self._process_send.setProcessChannelMode(
                    QtCore.QProcess.ProcessChannelMode.MergedChannels)
                self._process_send.start(ex, argss)
                self._send_in_progress = True
        else:
            self._process_send.kill()
            self._send_in_progress = False
            self._enable_interface_elements()
            if not self._serial_closed and self.pttGroupBox.isEnabled():
                self.pttReleasedRadioButton.setChecked(True)

    def receive_file(self) -> None:
        if not self._receive_in_progress:
            if not self._receive_filename:
                self.choose_recv_file()
            if self._receive_filename:
                if self._tool:
                    ex = "gg-transfer"
                    argss = "receive -f -w -o".split(" ")
                    # noinspection PyTypeChecker
                    argss.append(self._receive_filename)
                else:
                    ex = "quiet-transfer"
                    argss = (f"receive -f -p {self._quiet_protocol_list[self._quiet_protocol]}"
                             f" -w -o").split(" ")
                    # noinspection PyTypeChecker
                    argss.append(self._receive_filename)
                # if not self._serial_closed and self.pttGroupBox.isEnabled():
                #     self.pttPressedRadioButton.setChecked(True)
                self._process_receive.setProcessChannelMode(
                    QtCore.QProcess.ProcessChannelMode.MergedChannels)
                self._process_receive.start(ex, argss)
                self._receive_in_progress = True
        else:
            self._process_receive.kill()
            self._receive_in_progress = False
            self._enable_interface_elements()
            # if not self._serial_closed and self.pttGroupBox.isEnabled():
            #     self.pttReleasedRadioButton.setChecked(True)

    def send_text(self) -> None:
        if not self._send_in_progress:
            msg = self.shortMsg.text()
            if msg:
                self._tempfile, self._tempfilename = tempfile.mkstemp(text=False)
                os.write(self._tempfile, msg.encode("utf-8"))
                os.close(self._tempfile)
                if not self._serial_closed and self.pttGroupBox.isEnabled():
                    self.pttPressedRadioButton.setChecked(True)
                ex = "gg-transfer"
                argss = f"send -p {self._protocol} -i {self._tempfilename}".split(" ")
                self._process_send_msg.setProcessChannelMode(
                    QtCore.QProcess.ProcessChannelMode.MergedChannels)
                self._process_send_msg.start(ex, argss)
                self._send_in_progress = True
        else:
            self._process_send_msg.kill()
            self._send_in_progress = False
            if not self._serial_closed and self.pttGroupBox.isEnabled():
                self.pttReleasedRadioButton.setChecked(True)
            self._enable_interface_elements()

    def receive_text(self) -> None:
        if not self._receive_in_progress:
            self._tempfile, self._tempfilename = tempfile.mkstemp(text=False)
            os.close(self._tempfile)
            ex = "gg-transfer"
            argss = f"receive -n 1 -w -o {self._tempfilename}".split(" ")
            self._process_receive_msg.setProcessChannelMode(
                QtCore.QProcess.ProcessChannelMode.SeparateChannels)
            self._process_receive_msg.start(ex, argss)
            self._receive_in_progress = True
        else:
            self._process_receive_msg.kill()
            self._receive_in_progress = False
            self._enable_interface_elements()

    def set_gg_protocol(self, protocol: int) -> None:
        self._gg_protocol = protocol

    def set_quiet_protocol(self, protocol: int) -> None:
        self._quiet_protocol = protocol

    def set_tool(self, tool: bool) -> None:
        self._tool = tool
        self.ggProtocolComboBox.setDisabled(not self._tool)
        self.quietProtocolComboBox.setDisabled(self._tool)

    def choose_recv_file(self) -> None:
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self._receive_filename = selected_files[0]
            short_fname = ('...' + self._receive_filename[-20:]) if len(
                self._receive_filename) > 20 else self._receive_filename
            self.receiveFileLineEdit.setText(short_fname)

    def choose_send_file(self) -> None:
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self._send_filename = selected_files[0]
            short_fname = ('...' + self._send_filename[-20:]) if len(
                self._send_filename) > 20 else self._send_filename
            self.sendFileLineEdit.setText(short_fname)

