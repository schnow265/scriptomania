#!/bin/bash

# Check if input file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_file_list>"
    exit 1
fi

# Output file
output_file="metadata.txt"

# Write initial metadata header
echo ";FFMETADATA1" > "$output_file"

# Process each audio file listed in the input text file
prev_end=0
while IFS= read -r audio_file; do
    # Get duration of audio file using ffmpeg
    duration=$(ffmpeg -i "$audio_file" -f null - 2>&1 | grep -oE 'time=[0-9:.]+' | tail -n1 | grep -oE '[0-9:.]+' | awk -F':' '{ print ($1 * 3600) + ($2 * 60) + $3 }')

    # Calculate start and end times
    start=$prev_end
    end=$(echo "$prev_end + $duration" | bc)

    # Write chapter metadata to output file
    echo "[CHAPTER]" >> "$output_file"
    echo "TIMEBASE=1/1000" >> "$output_file"
    echo "START=$(echo "$start * 1000" | bc)" >> "$output_file"
    echo "END=$(echo "$end * 1000" | bc)" >> "$output_file"

    # Update previous end time for the next iteration
    prev_end=$end

done < "$1"

echo "Metadata written to $output_file"
