#!/bin/bash

python3 -m nuitka --standalone main.py --plugin-enable=numpy --plugin-enable=pylint-warnings -o main.out --onefile
