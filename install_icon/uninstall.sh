#!/bin/bash

if [ -f "~/local/bin/winkeyerserial" ]; then
	rm ~/.local/bin/winkeyerserial
fi

xdg-icon-resource uninstall --size 64 k6gte-pywinkey

xdg-desktop-icon uninstall k6gte-winkeyerserial.desktop

xdg-desktop-menu uninstall k6gte-winkeyerserial.desktop

