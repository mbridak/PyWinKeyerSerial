# PyWinKeyerSerial
Talk to the WinKeyerSerial and WinKeyerUSB.

First binary release can be downloaded [here
](https://github.com/mbridak/PyWinKeyerSerial/releases/download/21.5.7/winkeyerserial)

Focusing on Linux.

requires Python 3, PyQt5

On first run the program writes a file `.pywinkeyer.json` to the root of your home directory.
This file contains the default serial device along with any saved messages. If your winkeyer doesn't happen to be /dev/ttyUSB0 choose the correct device in the upper left.

You may find it more reliable to not use /dev/ttyUSB device names since these can easily change between reboots or replugs. Instead use what's mapped inside /dev/serial/by-id/.
Just plug in your keyer and `ls /dev/serial/by-id` and note the device id. Then edit the `~/.pywinkeyer.json` file and change the device, resave and relaunch. 

My winkeyer USB mapped to `/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AB0M6Y6H-if00-port0`

Any time you edit a message field it is automatically resaved to the json file. 

The default speed is set to by polling the speedpots current state. The program watches for speedpot changes and sets the speed accordingly. I do realize some of you (WKMini) may not have a speedpot. You can change the speed via the onscreen widget.  

![It's a screenshot](https://github.com/mbridak/PyWinKeyerSerial/raw/main/pic/WINKEYERSCREEN.png)