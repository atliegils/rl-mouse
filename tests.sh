#!/bin/bash

CMD="./evaluator.py -b"
PLOT="./plotter.py -b"
ARGS="-l -m 30000 --round_limit 1000 -cr 2 -tr 5 -hr 1 -b --test"
CMD="./bootstrapper.py"
ARGS="--count_evals"

# ARGS: FOV, GRID SIZE
run () {
	a=1
	b=10
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
    echo $CMD $ARGS $ARGS2 $a
    $CMD $ARGS $ARGS2 $a
}

run "solutions/sarsa" 12
run "solutions/qlearn" 12
run "solutions/meta_P_Q" 12 
run "solutions/meta_Q_simple" 12
run "solutions/qplearn" 12
run "solutions/sarsa_bigger" 12
run "solutions/sarsa_smaller" 12

run "solutions/sarsa" 15
run "solutions/qlearn" 15
run "solutions/meta_P_Q" 15 
run "solutions/meta_Q_simple" 15
run "solutions/qplearn" 15
run "solutions/sarsa_bigger" 15
run "solutions/sarsa_smaller" 15

run "solutions/sarsa" 
run "solutions/qlearn" 
run "solutions/meta_P_Q"  
run "solutions/meta_Q_simple" 
run "solutions/qplearn" 
run "solutions/sarsa_bigger" 
run "solutions/sarsa_smaller" 

