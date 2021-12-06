#! /bin/bash -xe

cbmc \
    --depth 512\
    --pointer-check\
    --memory-leak-check\
    --bounds-check\
    --div-by-zero-check\
    --signed-overflow-check\
    --pointer-overflow-check\
    --unsigned-overflow-check\
    --conversion-check\
    --undefined-shift-check\
    --float-overflow-check\
    --nan-check\
    --pointer-primitive-check\
    -DPROVERS -DPROVERS_CBMC\
    /mount/${1}/${2}.c
