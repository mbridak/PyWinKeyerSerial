#!/bin/bash

if [ -f "../dist/winkeyerserial" ]; then
    cp ../dist/winkeyerserial ~/.local/bin/
fi

xdg-icon-resource install --size 64 --context apps --mode user k6gte-pywinkey.png k6gte-pywinkey

xdg-desktop-icon install k6gte-winkeyerserial.desktop

xdg-desktop-menu install k6gte-winkeyerserial.desktop

