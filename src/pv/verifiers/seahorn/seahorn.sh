#! /bin/sh

sea bpf -g --cpu=1800 --bmc="${BMC}" --crab --track=mem --dsa=sea-cs -m64 -DPROVERS -DPROVERS_SEAHORN /mount/${1}/${2}.c
