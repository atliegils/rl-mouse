#!/bin/bash

CMD="./evaluator.py -b"
PLOT="./plotter.py -b"
ARGS="-l -m 30000 --round_limit 1000 -cr 2 -tr 5 -hr 1 -b --test"
CMD="./bootstrapper.py"
ARGS="--count_evals"

# ARGS: GRID SIZE
run () {
	a=1
	b=10
	s=200
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

	ARGS2="-g $b"
    echo $CMD $ARGS $ARGS2 $a --max_count $s
    $CMD $ARGS $ARGS2 $a
}

run "solutions/sarsa" 12 200
run "solutions/qlearn" 12 200
run "solutions/meta_Q_simple" 12 200
run "solutions/sarsa" 15 200
run "solutions/qlearn" 15 200
run "solutions/meta_Q_simple" 15 200
run "solutions/sarsa" 10 200
run "solutions/qlearn" 10 200
run "solutions/meta_Q_simple" 10 200

