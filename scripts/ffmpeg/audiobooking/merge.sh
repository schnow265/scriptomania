ls | grep "mp3" | awk '{printf "file |%s|\n", $0}' | sed -e "s/|/\'/g" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp3
ffmpeg -i output.mp3 output.m4a
