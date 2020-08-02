#!/bin/bash

echo '--- Print Input Args ---'

echo $@
echo $#
echo $1
echo $2
echo $3

left_dir=$1
right_dir=$2
extentions=`echo $3 | sed 's#,#\\\|#g'`
echo "$left_dir $right_dir $extentions"
echo ''

echo '--- List Left Files ---'

archives=(`ls -1 $left_dir | sed 's# #?_?#g'`)
#echo "All files: ${archives[@]}"
echo "Archive number: ${#archives[@]}"
echo ''

echo '--- Check Each File ---'

for archive in ${archives[@]}; do
  archive_name=`echo $archive | sed 's#?_?# #g'`
  echo "Archive name: $archive_name"

  left_path="$left_dir$archive_name/"
  right_path="$right_dir$archive_name/"
  echo "Archive path: $left_path $right_path"

  if [ ! -e "$right_path" ]; then
    mkdir -p "$right_path"
  fi

  files=`find "$left_path" -regex '.*\('$extentions'\)' | sed -e 's# #?_?#g' -e 's#.*/##g'`
  for file in $files; do
    filename=`echo $file | sed 's#?_?# #g'`
    echo "File name: $filename"

    left_file="$left_path$filename"
    right_file="$right_path$filename"

    left_size=`du -sb "$left_file" | awk '{print $1}'`
    right_size=''
    if [ -e "$right_file" ]; then
      right_size=`du -sb "$right_file" | awk '{print $1}'`
    fi

    echo "Left File[$left_file] size[$left_size]"
    echo "Right File[$right_file] size[$right_size]"

    should_override=false
    if [ -z "$right_size" ]; then
      echo 'Target file not exist!'
      should_override=true
    elif [ "$left_size" != "$right_size" ]; then
      echo 'Target file not match!'
      should_override=true
    fi

    if [ "$should_override" = true ]; then
      echo 'Copying...'
      cp -rf "$left_file" "$right_path"
      echo "Copy file[$left_file] into[$right_path] done"
    fi
  done

  echo ''
done
