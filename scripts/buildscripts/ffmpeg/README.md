# scriptomania-buildscripts-ffmpeg

## What does this do?

This builds ``ffmpeg`` with **all** optional and nonfree codecs. The base is the latest ffmpeg snapshot source build. Will dump sources in ``~/ffmpeg_sources`` and place the installed libraries in ``~/ffmpeg_bin`` and the resulting binaries will be in the ``~/bin`` folder.

## Important Information

This script was intended for CentOS/RHEL/Fedora.

### The two scripts

This folder contains three files:

- ``build.sh``, which builds ffmpeg
- ``update.sh``, which you need to run when you want to update your homegrown ffmpeg build to the latest version.
- ``ulti.sh``, which throws as much codecs as possible into ffmpeg.
## Other Links

- [ffmpeg compilation guide](https://trac.ffmpeg.org/wiki/CompilationGuide/Centos)
