#!/bin/bash

# Create the "out" folder if it doesn't exist
mkdir -p out

for file in *.txt; do
    if [ -f "$file" ]; then
        # Create a backup before modifying the file
        cp "$file" "$file.bak"

        # Remove single quotes
        sed -i "s/'//g" "$file"

        # Remove double quotes
        sed -i 's/"//g' "$file"

        # Remove "file" and "file:"
        sed -i 's/file//g; s/file://g' "$file"

        # Remove colons
        sed -i 's/://g' "$file"

        # Remove leading spaces
        sed -i 's/^[[:space:]]*//' "$file"

        # Remove both "file '" and "file: '" from each line
        sed -i "s/^file: '//; s/^file '//; s/$/'//; s/'$//" "$file"
        sed -i "s/^/file '/;s/$/'/" "$file"
        
        echo "Processing $file"

        # Extract filename without extension
        filename_no_ext=$(basename -- "$file" .txt)

        # Run ffmpeg command and place output files in the "out" folder
        ffmpeg -f concat -safe 0 -i "$file" -c copy "out/$filename_no_ext.mkv"
    fi
done
