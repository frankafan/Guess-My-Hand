#!/bin/bash
#
# Call with:
# `nohup ./tests.sh &
# to run in detached mode
#
# This allows you to let the script continue execution
# after you've disconnected from the SSH session

cat results.log >>old.results.log
echo -n "" >results.log

for i in {10..20}; do
	ROUNDS="$(("2" ** $i))"
	echo "starting $ROUNDS rounds at $(date)" >>results.log
	python3 Guess-my-Hand.py --nsGuesses 3 --nsStrategy 3 --nSims $ROUNDS >>results.log
	echo "Finished $ROUNDS rounds at $(date)" >>results.log
done
