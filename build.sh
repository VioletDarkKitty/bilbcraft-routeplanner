#!/bin/bash

if [ ! -d venv ]; then
  python3 -m venv venv
fi
. venv/bin/activate
pip3 install nuitka
pip3 install orderedset
pip3 install zstandard
./build_ui.sh
python3 -m nuitka --standalone main.py --enable-plugin=numpy --enable-plugin=pyside6 --nofollow-import-to=tkinter --follow-imports --prefer-source-code --plugin-enable=pylint-warnings -o main.out --onefile
