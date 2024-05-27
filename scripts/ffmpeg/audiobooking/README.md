# scriptomania-ffmpeg-audiobooking

## What does this do?

These two scripts will build a chpter list and merge all chapter files together.
To burn the metadata of the chapters into the file, run the following command. Output file anmes didn't change.

```shell
ffmpeg -i output.m4a -i metadata.txt -map 0 -map_metadata 1 -c copy output.m4b
```
