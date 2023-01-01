#!/bin/bash

python3 -m nuitka --standalone main.py --enable-plugin=numpy --enable-plugin=pyside6 --follow-imports --prefer-source-code --plugin-enable=pylint-warnings -o main.out --onefile
