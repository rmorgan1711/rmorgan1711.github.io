#!/bin/bash

# Based on 
# https://apple.stackexchange.com/questions/143639/app-to-organize-my-photos-into-folders-by-date

# https://ss64.com/osx/stat.html
# https://stackoverflow.com/questions/13210880/replace-one-substring-for-another-string-in-shell-script

dir=/Users/Bowen/Desktop/imports-2021-01-02

find "$dir" -maxdepth 1 -type f | while IFS= read -r file; do
    # file=${file/\.heic/\.HEIC}
    # file=${file/\.jpeg/\.JPG}
    # file=${file/\.png/\.PNG}
    # echo $file

    year=$(stat -f "%Sm" -t "%Y" "$file")
    month=$(stat -f "%Sm" -t "%m" "$file")
    [[ ! -d "$dir/$year/$month" ]] && mkdir -p "$dir/$year/$month"; 
    mv "$file" "$dir/$year/$month"
done
