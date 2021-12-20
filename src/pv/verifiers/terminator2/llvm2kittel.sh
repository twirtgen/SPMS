#!/bin/bash

L=($(echo "${1}" | sed $'s/\// /g'))
./llvm2kittel --eager-inline --dump-ll --no-slicing --t2 --function "${L[-1]}" /mount/${1}.bc > /mount/${1}.t2
