#! /bin/bash -xe

L=($(echo "${1}" | sed $'s/\// /g'))
clang -DPROVERS -DPROVERS_T2 -Wall -Wextra -c -emit-llvm -O0 /mount/${1}.c -o "/output/${L[-1]}.bc"
