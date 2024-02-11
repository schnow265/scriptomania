# scriptomania-ffmpeg-merger

## What does this do?

Have you ever had this problem: You need to merge a bunch of TV show episodes but they aren't organized (For example if you git em from YT)? But you can find yourself writing text files or have even automated it using a script?
What this script does is:

0. Make a backup (``{original_filename}.bak``)
1. Crawl through every txt file
2. Remove single quotes and double quotes
3. Removes ``file`` and ``file:``
4. Removes colons
5. Removes leading spaces
6. Removes ``file '`` and ``file: '`` from each line
7. Saves the filename without the extention in a variable
8. Runs a ffmpeg script to merge those two togeter and name the file after the variable ceated in Step 7 and place it in the ``out/`` folder.

## Cleanup

After a successful operation you will find to have a lot of ``.bak`` files in your folder. Just run ``rm -rf *.bak`` to clean those up.
