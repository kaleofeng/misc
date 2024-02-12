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

#ls $dir | awk "{x=\$0; gsub(/$src/, \"$dst\"); print \"mv \"x\" \"\$0}" | sh

for file in "$dir"/*; do
    new_name=$(echo "$file" | awk -v src="$src" -v dst="$dst" '{new=gensub(src, dst, "g"); if (new != $0) print new}')
    if [ -n "$new_name" ]; then
        cmd="mv '$file' '$new_name'"
        echo "$cmd"
        eval "$cmd"
    fi
done