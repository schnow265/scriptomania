{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation rec {
  pname = "ffmpeg";
  version = "7.0.1"; # Specify the FFmpeg version you want to build

  src = pkgs.fetchurl {
    url = "https://ffmpeg.org/releases/ffmpeg-${version}.tar.bz2";
    sha256 = "XnfoS2Q01lYQb6/jvOzMdxdkSQFPProk0z2z+9CTnck="; # Update with the correct hash
  };

  buildInputs = [
    pkgs.yasm
    pkgs.nasm
    pkgs.x264
    pkgs.x265
    pkgs.fdk_aac
    pkgs.lame
    pkgs.opusTools
    pkgs.libvpx
    pkgs.libtheora
    pkgs.libvorbis
    pkgs.libvmaf
    pkgs.libbluray
    pkgs.v4l-utils
    pkgs.openjpeg
    pkgs.intel-media-sdk
    pkgs.librsvg
    pkgs.fribidi
    pkgs.xorg.libxcb
    pkgs.xorg.xcbutil
    pkgs.xorg.xcbutilwm
    pkgs.xorg.xcbutilimage
    pkgs.freetype
    pkgs.fontconfig
    pkgs.libxml2
    pkgs.alsa-lib
    pkgs.SDL2
    pkgs.speex
    pkgs.libwebp
    pkgs.zimg
    pkgs.rubberband
    pkgs.xorg.xcbproto
    pkgs.xorg.xcbutil
    pkgs.xorg.xcbutilkeysyms
    pkgs.xorg.xcbutilrenderutil
  ];

  configurePhase = ''
    ./configure \
      --prefix=$out \
      --enable-gpl \
      --enable-nonfree \
      --enable-libx264 \
      --enable-libx265 \
      --enable-libfdk_aac \
      --enable-libmp3lame \
      --enable-libopus \
      --enable-libvpx \
      --enable-libtheora \
      --enable-libvorbis \
      --enable-libvmaf \
      #--enable-libbluray \
      --enable-libv4l2 \
      --enable-libopenjpeg \
      --enable-libmfx \
      --enable-librsvg \
      --enable-libfribidi \
      --enable-libxcb \
      --enable-libfreetype \
      --enable-libfontconfig \
      --enable-libxml2 \
      --enable-alsa \
      --enable-sdl2 \
      --enable-libspeex \
      --enable-libwebp \
      --enable-libzimg \
      --enable-librubberband
  '';

  buildPhase = "make";

  installPhase = "make install";
}
