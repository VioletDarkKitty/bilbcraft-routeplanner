#!/bin/bash

for f in *.ui
do
	echo $f
	pyside6-uic -g python $f > src/ui_$(basename $f ".ui").py
done
