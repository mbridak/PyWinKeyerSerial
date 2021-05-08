# PyWinKeyerSerial

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  [![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)  [![Made With:PyQt5](https://img.shields.io/badge/Made%20with-PyQt5-red)](https://pypi.org/project/PyQt5/)

Talk to the WinKeyerSerial, WinKeyerUSB and WKMini.

First binary release can be downloaded [here
](https://github.com/mbridak/PyWinKeyerSerial/releases/download/21.5.7/winkeyerserial)

Focusing on Linux.

Have the Winkeyer device plugged in before starting this program.

On first run the program writes a file `.pywinkeyer.json` to the root of your home directory.
This file contains the default serial device along with any saved messages. If your winkeyer doesn't happen to be /dev/ttyUSB0 choose the correct device in the upper left.

Any time you edit a message field, it is automatically resaved to the json file. 

The default speed is set to by polling the speedpots current state. The program watches for speedpot changes and sets the speed accordingly. I do realize some of you (WKMini) may not have a speedpot. You can change the speed via the onscreen widget.  

![It's a screenshot](https://github.com/mbridak/PyWinKeyerSerial/raw/main/pic/WINKEYERSCREEN.png)
