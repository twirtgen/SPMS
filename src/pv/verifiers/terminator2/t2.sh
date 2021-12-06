#! /bin/bash -xe

mono /T2/src/obj/x86/Debug/T2.exe --input_t2=/mount/"${1}.t2" --termination -print_proof
