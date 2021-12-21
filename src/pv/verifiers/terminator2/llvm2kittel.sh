#!/bin/bash

L=($(echo "${1}" | sed $'s/\// /g'))
./rewrite_kittel.py < $(./llvm2kittel --eager-inline -increase-strength -no-slicing --t2 --function "${L[-1]}" /mount/${1}.bc) > /mount/${1}.t2

