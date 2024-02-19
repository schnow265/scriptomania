#!/bin/bash

# Input audio file
input_file="input_audio_file.mp3"

# Create output directory if it doesn't exist
mkdir -p out

# Get chapters from input audio file
chapters=$(ffprobe -v quiet -show_chapters -of json "$input_file" | jq -r '.chapters[]')

# Loop through each chapter
while IFS= read -r chapter; do
    # Extract chapter start time and end time
    start_time=$(echo "$chapter" | jq -r '.start_time')
    end_time=$(echo "$chapter" | jq -r '.end_time')

    # Extract chapter name
    chapter_name=$(echo "$chapter" | jq -r '.tags.title')

    # Define output file name based on chapter name
    output_file="out/${chapter_name}.mp3"

    # Split audio file at chapter start time and end time and name the output file
    ffmpeg -i "$input_file" -vn -ss "$start_time" -to "$end_time" -acodec copy "$output_file"

done <<< "$chapters"