#!/bin/bash

# Install development tools and basic dependencies
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y git wget cmake autoconf automake libtool \
  bzip2 bzip2-devel freetype-devel fribidi-devel gnutls-devel \
  gsm-devel lame-devel libass-devel libtheora-devel libvorbis-devel \
  xz-devel numactl-devel nasm yasm pkgconfig meson ninja-build

# Create a directory for the source code
mkdir -p ~/ffmpeg_sources
cd ~/ffmpeg_sources

# Clone and build libaom (AV1 codec)
git clone --depth 1 https://aomedia.googlesource.com/aom
mkdir -p aom_build
cd aom_build
cmake ../aom -DENABLE_SHARED=off -DCMAKE_BUILD_TYPE=Release
make
sudo make install
cd ..

# Clone and build SVT-AV1 (another AV1 codec)
git clone --branch v1.0.0 --depth 1 https://gitlab.com/AOMediaCodec/SVT-AV1.git
cd SVT-AV1/Build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
sudo make install
cd ../..

# Clone and build dav1d (AV1 decoder)
git clone --depth 1 https://code.videolan.org/videolan/dav1d.git
mkdir -p dav1d_build
cd dav1d_build
meson setup .. --buildtype release --default-library static
ninja
sudo ninja install
cd ..

# Clone and build libzimg (scaling and conversion library)
git clone --depth 1 https://github.com/sekrit-twc/zimg.git
cd zimg
./autogen.sh
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# Clone and build other optional dependencies

# libfdk-aac
git clone --depth 1 https://github.com/mstorsjo/fdk-aac
cd fdk-aac
autoreconf -fiv
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libopus
git clone --depth 1 https://gitlab.xiph.org/xiph/opus.git
cd opus
./autogen.sh
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libvpx
git clone --depth 1 https://chromium.googlesource.com/webm/libvpx
cd libvpx
./configure --prefix="/usr/local" --disable-examples --disable-unit-tests --disable-shared
make
sudo make install
cd ..

# x264
git clone --depth 1 https://code.videolan.org/videolan/x264.git
cd x264
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# x265
hg clone https://bitbucket.org/multicoreware/x265
cd x265/build/linux
cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="/usr/local" -DENABLE_SHARED=off ../../source
make
sudo make install
cd ../../..

# libsoxr (SoX resampler library)
git clone https://github.com/chirlu/soxr.git
cd soxr
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX="/usr/local"
make
sudo make install
cd ../..

# libbluray
git clone --depth 1 https://code.videolan.org/videolan/libbluray.git
cd libbluray
./bootstrap
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libbs2b
git clone --depth 1 https://github.com/alex-gee/libbs2b.git
cd libbs2b
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libcaca
git clone --depth 1 https://github.com/cacalabs/libcaca.git
cd libcaca
./bootstrap
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libcdio
git clone --depth 1 https://git.savannah.gnu.org/git/libcdio.git
cd libcdio
./bootstrap
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libdrm
git clone --depth 1 https://gitlab.freedesktop.org/mesa/drm.git
cd drm
meson setup build --prefix=/usr/local --libdir=lib --default-library=static
meson compile -C build
sudo meson install -C build
cd ..

# libkvazaar
git clone --depth 1 https://github.com/ultravideo/kvazaar.git
cd kvazaar
./autogen.sh
./configure --prefix="/usr/local" --disable-shared
make
sudo make install
cd ..

# libmfx
git clone --depth 1 https://github.com/lu-zero/mfx_dispatch.git
cd mfx_dispatch
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make
sudo make install
cd ../..

# openh264
git clone --depth 1 https://github.com/cisco/openh264.git
cd openh264
make -j4
sudo make install PREFIX=/usr/local
cd ..

# openjpeg
git clone --depth 1 https://github.com/uclouvain/openjpeg.git
cd openjpeg
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local
make
sudo make install
cd ../..

# librubberband
git clone --depth 1 https://github.com/breakfastquay/rubberband.git
cd rubberband
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local
make
sudo make install
cd ../..

# libspeex
git clone --depth 1 https://gitlab.xiph.org/xiph/speex.git
cd speex
./autogen.sh
./configure --prefix=/usr/local --disable-shared
make
sudo make install
cd ..

# libzvbi
git clone --depth 1 https://gitlab.freedesktop.org/zvbi/libzvbi.git
cd libzvbi
./autogen.sh
./configure --prefix=/usr/local --disable-shared
make
sudo make install
cd ..

# ffmpeg
git clone --depth 1 https://git.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg
./configure --prefix="/usr/local" --pkg-config-flags="--static" \
  --extra-cflags="-I/usr/local/include" --extra-ldflags="-L/usr/local/lib" \
  --extra-libs="-lpthread -lm" --bindir="/usr/local/bin" \
  --enable-gpl --enable-nonfree --enable-libfdk_aac --enable-libfreetype \
  --enable-libfribidi --enable-libmp3lame --enable-libopus --enable-libtheora \
  --enable-libvpx --enable-libx264 --enable-libx265 --enable-libaom --enable-libsvtav1 \
  --enable-libbz2 --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio \
  --enable-libdrm --enable-libkvazaar --enable-libmfx --enable-libopenh264 \
  --enable-libopenjpeg --enable-librubberband --enable-libsoxr --enable-libspeex \
  --enable-libzimg --enable-libzvbi --enable-libdav1d
make
sudo make install

# Refresh shared library cache
sudo ldconfig

# Verify ffmpeg installation
ffmpeg -version

echo "FFmpeg and its dependencies have been successfully installed!"
