#!/usr/bin/env python3

import sys, os
import serial
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

class winkeyer(QtWidgets.QMainWindow):
    version = 0
    device = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0'
    oldtext = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(self.relpath("main.ui"), self)
        self.sendmsg1_button.clicked.connect(self.sendmsg1)
        self.sendmsg2_button.clicked.connect(self.sendmsg2)
        self.sendmsg3_button.clicked.connect(self.sendmsg3)
        self.sendmsg4_button.clicked.connect(self.sendmsg4)
        self.sendmsg5_button.clicked.connect(self.sendmsg5)
        self.sendmsg6_button.clicked.connect(self.sendmsg6)
        self.inputbox.textChanged.connect(self.handleTextChange)
        self.port = serial.Serial(self.device, 1200, timeout=1)
        self.port.setDTR(True)
        self.port.setRTS(False)
        self.host_open()

    def relpath(self, filename):
        """
        This is used if run as a pyinstaller packaged application.
        So the app can find the temp files.
        """
        try:
            base_path = sys._MEIPASS # pylint: disable=no-member
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

    def host_open(self):
        self.host_close()
        time.sleep(1)
        command = b'\x00\x02'
        self.port.write(command)
        self.version = self.port.read()

    def host_close(self):
        command = b'\x00\x03'
        self.port.write(command)

    def setspeed(self, speed):
        command=chr(2)+chr(speed)
        print(command.encode())
        self.port.write(command.encode())

    def setmode(self):
        command = b'\x0e\x44'
        self.port.write(command)

    def sendblended(self, msg):
        command = b'\x1b'+msg.upper().encode()
        self.port.write(command)

    def send(self, msg):
        command = msg.upper().encode()
        self.port.write(command)

    def sendBackspace(self):
        command = b'\x08'
        self.port.write(command)

    def tuneon(self):
        command = b'\x0b\x01'
        self.port.write(command)

    def tuneoff(self):
        command = b'\x0b\x00'
        self.port.write(command)

    def sendmsg1(self):
        print("sending1")
        #command = b'\x00\x0e\x01'
        #self.port.write(command)
        message=self.msg1.text()
        self.port.write(message.upper().encode())

    def sendmsg2(self):
        print("sending2")
        message=self.msg2.text()
        self.port.write(message.upper().encode())

    def sendmsg3(self):
        print("sending3")
        message=self.msg3.text()
        self.port.write(message.upper().encode())

    def sendmsg4(self):
        print("sending4")
        message=self.msg4.text()
        self.port.write(message.upper().encode())

    def sendmsg5(self):
        print("sending5")
        message=self.msg5.text()
        self.port.write(message.upper().encode())

    def sendmsg6(self):
        print("sending6")
        message=self.msg6.text()
        self.port.write(message.upper().encode())

    def handleTextChange(self):
        newtext = self.inputbox.toPlainText()
        if len(newtext) < len(self.oldtext):
            self.sendBackspace()
            self.oldtext = newtext
            return
        self.send(newtext[len(self.oldtext):])
        self.oldtext = newtext

    def getwaiting(self):
        if self.port.in_waiting:
            byte = self.port.read()
            if (byte[0] & b'\xc0'[0]) == b'\xc0'[0]: #Status Change
                print(f"Status Change: {byte}")
                pass
            elif (byte[0] & b'\xc0'[0]) == b'\x80'[0]: #speed pot change
                print(f"Pot change: {byte}")
                pass
            else:
                self.outputbox.insertPlainText(f"{byte.decode()}")
                #process echoback character
                print(f"Echo Char: {byte}")
                pass


app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
keyer = winkeyer()
keyer.show()
#print(f"version: {keyer.version}")
keyer.setmode()
keyer.setspeed(18)
#keyer.send('HELLO')
#keyer.sendblended('SK')
#keyer.sendmsg()
#while True:
#    keyer.getwaiting()
#keyer.host_close()
timer = QtCore.QTimer()
timer.timeout.connect(keyer.getwaiting)
timer.start(50)

app.exec()
