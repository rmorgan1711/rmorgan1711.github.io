#!/bin/bash

# Based on 
# https://apple.stackexchange.com/questions/143639/app-to-organize-my-photos-into-folders-by-date

# https://ss64.com/osx/stat.html
# https://stackoverflow.com/questions/13210880/replace-one-substring-for-another-string-in-shell-script

dir=~/Desktop/the-relevant-folder

find "$dir" -maxdepth 1 -type f | while IFS= read -r file; do

    year=$(stat -f "%SB" -t "%Y" "$file")
    month=$(stat -f "%SB" -t "%m" "$file")
    [[ ! -d "$dir/$year/$month" ]] && mkdir -p "$dir/$year/$month"; 
    mv "$file" "$dir/$year/$month"
done

# pic-migrate/ contains folders of years of photos
# trailing slash is important in cp command
cd /Volumes/device-name/pics-vids-music
cp -Rnp /Users/Bowen/Desktop/pic-migrate/ Pictures