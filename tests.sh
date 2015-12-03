#!/bin/bash

PLOT="./plotter.py -b"
CMD="./bootstrapper.py"
ARGS="--count_evals"

# ARGS: GRID SIZE
run () {
	a=1
	b=10
	s=200
	d=1
	args3=""
	args4=""
	args5=""
	args6=""

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
		s=$3
	fi
	shift
	shift
	shift

	OUT=${a}_${b}_${s}_$*

	ARGS2="-g $b"
    echo $CMD $ARGS $ARGS2 $a --max_count $s $* --outfile reval_solutions/$OUT.txt
    $CMD $ARGS $ARGS2 $a --max_count $s $* --outfile $OUT
}

run "qlearn" 12 250
run "meta_Q_simple" 12 250
run "sarsa_norand" 12 250
run "sarsa" 12 250
run "meta_simple" 12 250

run "omni_q" 15 250
run "omni" 15 250
run "qlearn" 15 250
run "meta_Q_simple" 15 250
run "sarsa_norand" 15 250
run "sarsa" 15 250
run "meta_simple" 15 250
