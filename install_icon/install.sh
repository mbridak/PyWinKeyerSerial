#!/bin/bash

cp ../dist/winkeyerserial ~/.local/bin/

xdg-icon-resource install --size 64 --context apps --mode user k6gte-pywinkey.png k6gte-pywinkey

xdg-desktop-icon install k6gte-winkeyerserial.desktop

xdg-desktop-menu install k6gte-winkeyerserial.desktop

