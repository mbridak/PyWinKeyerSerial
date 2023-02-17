#!/usr/bin/env python3
"""
Who's at fault here: K6GTE, Mike Bridak
Where can you yell at me: michael.bridak@gmail.com
where can I get updates?: https://github.com/mbridak/PyWinKeyerSerial

This program talks to the WinKeyerUSB and WinKeyerSerial devices by K1EL.
It sends what you type to the keyer, and sends presaved messages when you press the
appropriate button.

The first time you run this program it creates a file '.pywinkeyer.json'
in the root of your home directory. This file is used to store the default serial
device and the presaved messages.

When you update the presaved message fields they are resaved automatically.

The speed is initially set by polling the speed pot.

The speed pot should work to change the code speed on the fly.

This is where I realized that not all K1EL keyers have a speedpot on them....

You really should have gotten the one with the speedpot.....
"""

# pylint: disable=no-name-in-module, c-extension-no-member, global-statement, bare-except

import sys
import os
import json
import time
import pkgutil
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import logging


import serial
from serial.tools.list_ports import comports

# from PyQt5.QtSerialPort import QSerialPort
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread

logging.basicConfig(level=logging.WARNING)

MESSAGE = ""


class RequestHandler(SimpleXMLRPCRequestHandler):
    """Doc String"""

    rpc_paths = ("/RPC2",)


class RPCThread(QThread):
    """Doc String"""

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.server = None

    def run(self):
        """Doc String"""
        # sleep a little bit to make sure QApplication is running.
        self.sleep(1)
        print("--- starting server…")
        with SimpleXMLRPCServer(("0.0.0.0", 8000), allow_none=True) as self.server:
            self.server.register_function(k1elsendstring)
            self.server.register_introspection_functions()
            self.server.serve_forever()


class RPCWidget(QWidget):
    """Doc String"""

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.thread = RPCThread(self)
        self.thread.start()


def k1elsendstring(sss):
    """Doc String"""
    global MESSAGE
    MESSAGE = f"{sss} "


def load_fonts_from_dir(directory):
    """Load font families"""
    families_set = set()
    for thing in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
        _id = QFontDatabase.addApplicationFont(thing.absoluteFilePath())
        families_set |= set(QFontDatabase.applicationFontFamilies(_id))
    return families_set


class WinKeyer(QtWidgets.QMainWindow):
    """
    The main class
    """

    version = 0
    device = ""
    oldtext = ""
    port = None
    initialpot = False
    settings_dict = {"device": "", "1": "", "2": "", "3": "", "4": "", "5": "", "6": ""}

    def __init__(self, *args, **kwargs):
        """
        connects the widgets to their callbacks.
        queries for existing serial ports.
        loads in saved defaults.
        """
        self.working_path = os.path.dirname(
            pkgutil.get_loader("winkeyerserial").get_filename()
        )
        data_path = self.working_path + "/main.ui"
        super().__init__(*args, **kwargs)
        uic.loadUi(data_path, self)
        self.sendmsg1_button.clicked.connect(self.sendmsg1)
        self.sendmsg2_button.clicked.connect(self.sendmsg2)
        self.sendmsg3_button.clicked.connect(self.sendmsg3)
        self.sendmsg4_button.clicked.connect(self.sendmsg4)
        self.sendmsg5_button.clicked.connect(self.sendmsg5)
        self.sendmsg6_button.clicked.connect(self.sendmsg6)
        self.inputbox.textChanged.connect(self.handle_text_change)
        self.spinBox_speed.valueChanged.connect(self.spinboxspeed)
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.getwaiting)
        for serialport in comports():
            self.comboBox_device.addItem(serialport.device)
            index = self.comboBox_device.findText(serialport.device)
            self.comboBox_device.setItemData(
                index, serialport.description, Qt.ToolTipRole
            )
            self.device = serialport.device
            self.settings_dict["device"] = self.device
        self.comboBox_device.currentIndexChanged.connect(self.change_serial)
        self.loadsaved()

    def change_serial(self):
        """
        The serial device was changed via the onscreen widget.
        """
        self.settings_dict["device"] = self.comboBox_device.currentText()
        self.savestuff()
        self.device = self.settings_dict.get("device")
        self.host_init()
        if self.port:
            self.setmode()

    def loadsaved(self):
        """
        load saved default device and messages if they exist.
        otherwise write some sane defaults as a json text file in the users home directory.
        """
        home = os.path.expanduser("~")
        if os.path.exists(home + "/.pywinkeyer.json"):
            with open(
                home + "/.pywinkeyer.json", "rt", encoding="utf-8"
            ) as file_handle:
                self.settings_dict = json.loads(file_handle.read())
        else:
            with open(
                home + "/.pywinkeyer.json", "wt", encoding="utf-8"
            ) as file_handle:
                file_handle.write(json.dumps(self.settings_dict))
        self.device = self.settings_dict["device"]
        self.msg1.setText(self.settings_dict.get("1"))
        self.msg2.setText(self.settings_dict.get("2"))
        self.msg3.setText(self.settings_dict.get("3"))
        self.msg4.setText(self.settings_dict.get("4"))
        self.msg5.setText(self.settings_dict.get("5"))
        self.msg6.setText(self.settings_dict.get("6"))
        # connect the change events to resave messages
        self.msg1.textChanged.connect(self.savestuff)
        self.msg2.textChanged.connect(self.savestuff)
        self.msg3.textChanged.connect(self.savestuff)
        self.msg4.textChanged.connect(self.savestuff)
        self.msg5.textChanged.connect(self.savestuff)
        self.msg6.textChanged.connect(self.savestuff)

    def savestuff(self):
        """
        save state as a json file in the home directory
        """
        home = os.path.expanduser("~")
        self.settings_dict["1"] = self.msg1.text()
        self.settings_dict["2"] = self.msg2.text()
        self.settings_dict["3"] = self.msg3.text()
        self.settings_dict["4"] = self.msg4.text()
        self.settings_dict["5"] = self.msg5.text()
        self.settings_dict["6"] = self.msg6.text()
        with open(home + "/.pywinkeyer.json", "wt", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps(self.settings_dict))

    def host_init(self):
        """
        Opens the serial port and sets its parameters
        """
        self.outputbox.clear()
        self.comboBox_device.setCurrentIndex(self.comboBox_device.findText(self.device))
        try:
            if self.port:
                self.port.close()
            self.port = serial.Serial()
            self.port.port = self.device
            self.port.baudrate = 1200
            self.port.bytesize = serial.EIGHTBITS
            self.port.parity = serial.PARITY_NONE
            self.port.stopbits = serial.STOPBITS_TWO
            self.port.dsrdtr = True
            self.port.rtscts = False
            self.port.timeout = 0
            self.port.open()
            if not self.port.is_open:
                self.outputbox.insertPlainText(
                    f"Unable to open serial port: {self.device}"
                )
                return
        except serial.serialutil.SerialException:
            self.outputbox.insertPlainText(f"Unable to open serial port: {self.device}")
            self.port = False
            return
        self.host_open()

    def host_open(self):
        """
        Sends the open command to winkeyer so it will start listening to us.
        """
        self.host_close()
        time.sleep(1)  # wait for the keyer to reset.
        command = b"\x00\x02"
        self.port.write(command)
        time.sleep(0.5)
        self.version = self.port.read(255)
        if self.version == b"":  # No version... Maybe the wrong serial port was chosen.
            self.outputbox.clear()
            self.outputbox.insertPlainText(
                f"{self.device} is open but WinKeyer is not responding"
            )
        self.timer2.start(100)
        command = b"\x07"  # have the winkeyer return the pot speed setting
        self.port.write(command)

    def host_close(self):
        """
        Sends the close command to winkeyer
        """
        command = b"\x00\x03"
        self.port.write(command)

    def setspeed(self, speed):
        """
        Sets winkeyer speed. I believe valid speeds are from 5 to brainmelt
        """
        command = chr(2) + chr(int(speed))
        self.port.write(command.encode())
        self.spinBox_speed.setValue(int(speed))

    def potspeed(self, speed):
        """
        The pot speed value is the 6 LSB of the returned byte.
        It has the 2 MSB of the byte set to 10
        """
        self.setspeed(speed - 123)

    def spinboxspeed(self):
        """
        User changed the speed value in the spinbox.
        """
        self.setspeed(self.spinBox_speed.value())

    def setmode(self):
        """
        Basically tells the device 'Hey, well be expecting you to
        transform letters into boop-ity boop stuff.'
        """
        command = b"\x0e\x44"
        self.port.write(command)

    def sendblended(self, msg):
        """
        a way to glue togetther two characters to send a prosign.
        """
        command = b"\x1b" + msg.upper().encode()
        self.port.write(command)

    def send(self, msg):
        """
        Basic string in, Morse out of the device.
        """
        command = msg.upper().encode()
        self.port.write(command)

    def send_backspace(self):
        """
        Erases a character from the end of the winkeyer buffer if it has not been sent already.
        """
        command = b"\x08"
        self.port.write(command)

    def tuneon(self):
        """
        Keydown and hold it.
        """
        command = b"\x0b\x01"
        self.port.write(command)

    def tuneoff(self):
        """
        Stop the keydown
        """
        command = b"\x0b\x00"
        self.port.write(command)

    def sendmsg1(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        local_message = self.msg1.text()
        self.port.write(local_message.upper().encode())

    def sendmsg2(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        local_message = self.msg2.text()
        self.port.write(local_message.upper().encode())

    def sendmsg3(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        local_message = self.msg3.text()
        self.port.write(local_message.upper().encode())

    def sendmsg4(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        local_message = self.msg4.text()
        self.port.write(local_message.upper().encode())

    def sendmsg5(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        local_message = self.msg5.text()
        self.port.write(local_message.upper().encode())

    def sendmsg6(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        local_message = self.msg6.text()
        self.port.write(local_message.upper().encode())

    def handle_text_change(self):
        """
        This is a poorly handled function where it sends text you type in the big box to the keyer.
        But hey, you get what you pay for. If you can do better then have at it.
        Oh and send a pull request when your done.
        """
        newtext = self.inputbox.toPlainText()
        if len(newtext) < len(self.oldtext):
            self.send_backspace()
            self.oldtext = newtext
            return
        self.send(newtext[len(self.oldtext) :])
        self.oldtext = newtext

    def getwaiting(self):
        """
        Checks to see the keyer has data to send to us.
        Could be a status change.
        Could be the user has twisted that turney bit thingy with the knob on it.
        It could also be an echo of the last character it has sent or is sending.
        """
        try:
            if self.port.in_waiting:
                byte = self.port.read(1)
                if (byte[0] & b"\xc0"[0]) == b"\xc0"[0]:  # Status Change
                    # print(f"Status Change: {byte}")
                    pass
                elif (byte[0] & b"\xc0"[0]) == b"\x80"[0]:  # speed pot change
                    self.potspeed(byte[0])
                else:  # process echoback character
                    # print(byte.decode(), end="", flush=True)
                    self.outputbox.insertPlainText(f"{byte.decode()}")
        except:
            self.host_init()  # Some one may have unplugged the keyer.

    def checkmessage(self):
        """
        This is so hackish, it's a bit embarassing.
        This should be handled with slots and signals.
        But.... It works.
        """
        global MESSAGE
        sss = MESSAGE
        MESSAGE = ""
        if sss:
            self.port.write(sss.upper().encode())


app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")
PATH = os.path.dirname(pkgutil.get_loader("winkeyerserial").get_filename())
families = load_fonts_from_dir(PATH)
logging.info(families)
keyer = WinKeyer()
keyer.show()
keyer.host_init()
if keyer.port:
    keyer.setmode()
rpcwidget = RPCWidget()
timer = QTimer()
timer.timeout.connect(keyer.checkmessage)  # Do not do this.


def main():
    """Main entry"""
    os.system(
        "xdg-icon-resource install --size 32 --context apps --mode user "
        f"{PATH}/k6gte-winkeyerserial-32.png k6gte-winkeyerserial"
    )
    os.system(
        "xdg-icon-resource install --size 64 --context apps --mode user "
        f"{PATH}/k6gte-winkeyerserial-64.png k6gte-winkeyerserial"
    )
    os.system(
        "xdg-icon-resource install --size 128 --context apps --mode user "
        f"{PATH}/k6gte-winkeyerserial-128.png k6gte-winkeyerserial"
    )
    os.system(f"xdg-desktop-menu install {PATH}/k6gte-winkeyerserial.desktop")
    timer.start(250)
    app.exec()


if __name__ == "__main__":
    main()
