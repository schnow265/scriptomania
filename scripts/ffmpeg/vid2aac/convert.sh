for file in *.mp4; do
    # Check if the file exists
    if [ -e "$file" ]; then
        # Extract audio from each MP4 file
        ffmpeg -i "$file" -vn -acodec copy "${file%.mp4}.aac"
    else
        echo "File not found: $file"
    fi
done