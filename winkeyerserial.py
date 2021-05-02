#!/usr/bin/env python3

import sys, os
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5 import uic

class winkeyer(QtWidgets.QMainWindow):
    """
    The device below will need to be changed to your serial device id.
    I built the winkeyer serial kit and supplied my own serial device.

    I have a winkeyer usb on order. Will be curious to see what device they use.
    """
    version = 0
    device = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0'
    #device = '/dev/ttyUSB0'
    oldtext = ''
    port = ''

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

    def host_init(self):
        try:
            #self.port = serial.Serial(self.device, 1200, timeout=1)
            self.port = QSerialPort(self)
            self.port.setPortName(self.device)
            self.port.setBaudRate(QSerialPort.Baud1200)
            if self.port.open(QSerialPort.ReadWrite):
                self.port.setDataTerminalReady(True)
                self.port.setRequestToSend(False)
            else:
                self.outputbox.insertPlainText(f"Unable to open serial port: {self.device}")
                return
        except:
            self.outputbox.insertPlainText(f"Unable to open serial port: {self.device}")
            self.port = False
            return
        self.host_open()

    def host_open(self):
        """
        Sends the open command to winkeyer so it will start listening to us.
        """
        self.host_close()
        time.sleep(1) #the house of cards falls apart if this is removed...
        command = b'\x00\x02'
        self.port.write(command)
        self.port.waitForReadyRead()
        self.version = self.port.read(255)
        self.port.readyRead.connect(self.getwaiting)

    def host_close(self):
        command = b'\x00\x03'
        self.port.write(command)

    def setspeed(self, speed):
        """
        Sets winkeyer speed. I believe valid speeds are from 5 to brainmelt
        """
        command=chr(2)+chr(speed)
        self.port.write(command.encode())

    def potspeed(self, speed):
        self.setspeed(speed-123)
        self.potspeed_label.setText(f"{speed-123}")


    def setmode(self):
        """
        Basically tells the device 'Hey, well be expecting you to transform letters into boop-ity boop stuff.'
        """
        command = b'\x0e\x44'
        self.port.write(command)

    def sendblended(self, msg):
        """
        a way to glue togetther two characters to send a prosign.
        """
        command = b'\x1b'+msg.upper().encode()
        self.port.write(command)

    def send(self, msg):
        """
        Basic string in, Morse out of the device.
        """
        command = msg.upper().encode()
        self.port.write(command)

    def sendBackspace(self):
        """
        Erases a character from the end of the winkeyer buffer if it has not been sent already.
        """
        command = b'\x08'
        self.port.write(command)

    def tuneon(self):
        """
        Keydown and hold it.
        """
        command = b'\x0b\x01'
        self.port.write(command)

    def tuneoff(self):
        """
        Stop the keydown
        """
        command = b'\x0b\x00'
        self.port.write(command)

    def sendmsg1(self):
        """
        This and the following just pull text from the fields next to the button and sends it.
        """
        message=self.msg1.text()
        self.port.write(message.upper().encode())

    def sendmsg2(self):
        message=self.msg2.text()
        self.port.write(message.upper().encode())

    def sendmsg3(self):
        message=self.msg3.text()
        self.port.write(message.upper().encode())

    def sendmsg4(self):
        message=self.msg4.text()
        self.port.write(message.upper().encode())

    def sendmsg5(self):
        message=self.msg5.text()
        self.port.write(message.upper().encode())

    def sendmsg6(self):
        message=self.msg6.text()
        self.port.write(message.upper().encode())

    def handleTextChange(self):
        """
        This is a poorly handled function where it sends text you type in the big box to the keyer.
        But hey, you get what you pay for. If you can do better then have at it.
        Oh and send a pull request when your done.
        """
        newtext = self.inputbox.toPlainText()
        if len(newtext) < len(self.oldtext):
            self.sendBackspace()
            self.oldtext = newtext
            return
        self.send(newtext[len(self.oldtext):])
        self.oldtext = newtext

    def getwaiting(self):
        """
        Checks to see the keyer has data to send to us.
        Could be a status change.
        Could be the user has twisted that turney bit thingy with the knob on it.
        It could also be an echo of the last character it has sent or is sending.
        """
        try:
            byte = self.port.read(255)
            if (byte[0] & b'\xc0'[0]) == b'\xc0'[0]: #Status Change
                print(f"Status Change: {byte}")
            elif (byte[0] & b'\xc0'[0]) == b'\x80'[0]: #speed pot change
                self.potspeed(byte[0])
            else: #process echoback character
                self.outputbox.insertPlainText(f"{byte.decode()}")             
        except:
            self.host_init() #Some one may have unplugged the keyer.


app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
keyer = winkeyer()
keyer.show()
keyer.host_init()
if keyer.port:
    keyer.setmode()
    keyer.setspeed(18)
    #keyer.send('HELLO')
    #keyer.sendblended('SK')
    #timer = QtCore.QTimer()
    #timer.timeout.connect(keyer.getwaiting)
    #timer.start(50)
app.exec()
