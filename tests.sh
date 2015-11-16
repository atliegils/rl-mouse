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


	ARGS2="-g $b"
    echo $CMD $ARGS $ARGS2 $a --max_count $s $*
    $CMD $ARGS $ARGS2 $a --max_count $s $*
}
#run "solutions/sarsa" 12 250 --custom_actions "left,right,forward"
#run "solutions/qlearn" 12 250 --custom_actions "left,right,forward"
#run "solutions/meta_simple" 12 250 --custom_actions "left,right,forward"
#run "solutions/meta_Q_simple" 12 250 --custom_actions "left,right,forward"
#run "solutions/sarsa" 15 250 --custom_actions "left,right,forward"
#run "solutions/qlearn" 15 250 --custom_actions "left,right,forward"
#run "solutions/meta_simple" 15 250 --custom_actions "left,right,forward"
#run "solutions/meta_Q_simple" 15 250 --custom_actions "left,right,forward"
#run "solutions/sarsa" 10 250 --custom_actions "left,right,forward"
#run "solutions/qlearn" 10 250 --custom_actions "left,right,forward"
#run "solutions/meta_simple" 10 250 --custom_actions "left,right,forward"
#run "solutions/meta_Q_simple" 10 250 --custom_actions "left,right,forward"
#run "solutions/sarsa" 12 250 --custom_actions "left,right,forward,?"
#run "solutions/qlearn" 12 250 --custom_actions "left,right,forward,?"
#run "solutions/meta_simple" 12 250 --custom_actions "left,right,forward,?"
#run "solutions/meta_Q_simple" 12 250 --custom_actions "left,right,forward,?"

run "solutions/sarsa" 15 250 --custom_actions "left,right,forward,?"
run "solutions/qlearn" 15 250 --custom_actions "left,right,forward,?"
run "solutions/meta_simple" 15 250 --custom_actions "left,right,forward,?"
run "solutions/meta_Q_simple" 15 250 --custom_actions "left,right,forward,?"
run "solutions/sarsa" 10 250 --custom_actions "left,right,forward,?"
run "solutions/qlearn" 10 250 --custom_actions "left,right,forward,?"
run "solutions/meta_simple" 10 250 --custom_actions "left,right,forward,?"
run "solutions/meta_Q_simple" 10 250 --custom_actions "left,right,forward,?"

