#!/bin/bash

folder="compare_meta_flat"

mkdir $folder
mkdir $folder/txt
mkdir $folder/html

CMD="./evaluator.py -b"
PLOT="./plotter.py -b"
ARGS="-l -m 30000 --round_limit 1000 -cr 4 -tr 5 -hr 1 -b --test"

# ARGS: FOV, GRID SIZE
run () {
	a=1
	b=5
	d=1

	if [ "$1" ]
	then
		a=$1
	fi
	if [ "$2" ]
	then
		b=$2
	fi
	if [ "$3" ]
	then
		d=$3
	fi

	name="${a}_${b}x${b}_d${d}"
	n1="${name}-flat"
	n2="${name}-meta"
	ARGS2="-g $b --fov $a"
	echo $ARGS $ARGS2
    $CMD $ARGS $ARGS2 -o ${n1}.txt -d $d && $PLOT ${n1}.txt
    mv ${n1}.txt $folder/txt
    mv ${n1}.html $folder/html
    $CMD $ARGS $ARGS2 -o ${n2}.txt -d $d --meta && $PLOT ${n2}.txt
	mv ${n2}.txt $folder/txt
	mv ${n2}.html $folder/html
}

run 2 7 
run 3 10
run 3 11
run 3 12
run 3 15

