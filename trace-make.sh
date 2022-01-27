#! /bin/bash

export TRACE=make.trace

# redirect fd 100 to lock file
# exec 100>timing.lock

# record the pid, and the start time (s.ns), and the command make is running
echo B $$ `date +%s.%N` "[$*]" >> $TRACE

# the actual command make wants to run
bash "$@"

# record the pid and the end time (s.ns)
echo E $$ `date +%s.%N` >> $TRACE
