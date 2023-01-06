#!/bin/bash

. venv/bin/activate
pip3 install nuitka
pip3 install orderedset
pip3 install zstandard
python3 -m nuitka --standalone main.py --enable-plugin=numpy --enable-plugin=pyside6 --nofollow-import-to=tkinter --follow-imports --prefer-source-code --plugin-enable=pylint-warnings -o main.out --onefile
