#! /bin/bash

export TRACE=make.trace

# redirect fd 100 to lock file
# exec 100>timing.lock

# record the pid, the command make is running, and the start time 
echo "$$ [$*]" `date +%s` >> $TRACE

# the actual command make wants to run
bash "$@"

# record the pid, and the end time
echo $$ `date +%s` >> $TRACE