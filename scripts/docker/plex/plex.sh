docker run -d \
  --name=plex \
  --net=host \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Etc/UTC \
  -e VERSION=docker \
  -v /run/media/schnow265/E76C-D646/plexconfig:/config \ 
  -v /run/media/schnow265/E76C-D646/plexmedlib:/media \
  --restart none \
  lscr.io/linuxserver/plex:latest