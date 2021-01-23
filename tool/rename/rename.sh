#!/bin/bash

if [ $# -ne 3 ]; then
    printf "Rename filenames in batch\n"
    printf "Usage: rename [src] [dst] [dir]\n"
    printf ".e.g.: rename hallo hello ."
    exit 0
fi

src=$1
dst=$2
dir=$3

ls $dir | awk "{x=\$0; gsub(/$src/, \"$dst\"); print \"mv \"x\" \"\$0}" | sh
