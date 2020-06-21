#!/bin/bash

echo '--- Print Input Args ---'

echo $@
echo $#
echo $1
echo $2
echo ''

leftdir=$1
rightdir=$2

echo '--- List Left Files ---'

fns=(`ls -1 $leftdir | sed 's# #?_?#g'`)
echo "All files: ${fns[@]}"
echo "File number: ${#fns[@]}"
echo ''

echo '--- Check Each File ---'

for fn in ${fns[@]}; do
  filename=`echo $fn | sed 's#?_?# #g'`
  echo "File: $filename"

  leftfile="$leftdir/$filename"
  rightfile="$rightdir/$filename"
  echo "$leftfile $rightfile"

  if [ ! -e "$rightfile" ]; then
    echo "Target file [$rightfile] not exists, copy now..."
    cp -rf "$leftfile" "$rightdir"
    echo "Copy from [$leftfile] to [$rightdir] done"
  fi

  echo ''
done

echo '--- Remove All Images  ---'

find $rightdir -regex '.*\(nfo\|jpg\|png\)' | \
  xargs -n 1 -i rm -f {}
