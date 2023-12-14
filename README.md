# winkeyerserial

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  [![Python: 3.9+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)  [![Made With:PyQt5](https://img.shields.io/badge/Made%20with-PyQt5-red)](https://pypi.org/project/PyQt5/)![PyPI - Downloads](https://img.shields.io/pypi/dm/winkeyerserial)

![logo](https://github.com/mbridak/PyWinKeyerSerial/raw/main/winkeyerserial/k6gte.winkeyerserial.svg)

Talk to the K1EL WinKeyerSerial, WinKeyerUSB and WKMini.

It provides an API to control the WinKeyer. It listens for XMLRPC requests on port 8000.

The XMLRPC server exposes the following methods:

- k1elsendstring
- setspeed
- sendblended
- tuneon
- tuneoff

Have the Winkeyer device plugged in before starting this program.

On first run the program writes a file `.pywinkeyer.json` to the root of your home directory.
This file contains the default serial device along with any saved messages. If your winkeyer doesn't happen to be /dev/ttyUSB0 choose the correct device in the upper left.

Any time you edit a message field, it is automatically resaved to the json file.

The default speed is set to by polling the speedpots current state. The program watches for speedpot changes and sets the speed accordingly. I do realize some of you (WKMini) may not have a speedpot. You can change the speed via the onscreen widget.  

![It's a screenshot](https://github.com/mbridak/PyWinKeyerSerial/raw/main/pic/WINKEYERSCREEN.png)

## Installing, updating, running and removal

```bash
# install
pip install winkeyerserial

# update
pip install -U winkeyerserial

# run
winkeyerserial

# remove
pip uninstall winkeyerserial
```

## What's new

- [23-5-11] Added xmlrpc function to set speed.
- [23-2-17] Added serial device descriptions (hover tooltip) to the detected serial devices in the dropdown.
- Added an XMLRPC server. So now my [Winter Field Day](https://github.com/mbridak/WinterFieldDayLogger), [Field Day](https://github.com/mbridak/FieldDayLogger) and [K1USNSST](https://github.com/mbridak/k1usnsst) Loggers will be able to send CW macros to this. The interface for the client is dead simple:
 `xmlrpc.client.ServerProxy("http://localhost:8000").k1elsendstring("Hello World")`
 That's it...
