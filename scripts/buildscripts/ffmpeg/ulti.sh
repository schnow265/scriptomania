#!/bin/bash

# Define the directories
SOURCE_DIR=~/ffmpeg_sources
BUILD_DIR=~/ffmpeg_build

# Create the directories if they don't exist
mkdir -pv "$SOURCE_DIR"
mkdir -pv "$BUILD_DIR"

# Function to check if a lockfile exists
is_locked() {
    local component=$1
    local lockfile="$BUILD_DIR/$component.lock"
    [ -f "$lockfile" ]
}

# Function to create a lockfile
create_lock() {
    local component=$1
    local lockfile="$BUILD_DIR/$component.lock"
    touch "$lockfile"
}

# Install necessary build tools
sudo dnf install -y git autoconf automake cmake gcc gcc-c++ \
    libtool make nasm pkgconfig yasm zlib-devel xorg-x11-util-macros \
    gnutls-devel libunistring-devel openjpeg2-devel

# Enable RPMFusion repositories if not already enabled
sudo dnf install -y \
    https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
    https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Install codec libraries and dependencies from the repositories
sudo dnf install -y \
    x264-devel \
    x265-devel \
    fdk-aac-devel \
    lame-devel \
    opus-devel \
    libvpx-devel \
    libass-devel \
    libtheora-devel \
    libvorbis-devel \
    libvmaf-devel \
    libbluray-devel \
    libv4l-devel \
    openjpeg2-devel \
    libmfx-devel \
    librsvg2-devel \
    fribidi-devel \
    libxcb-devel \
    xcb-util-devel \
    xcb-util-wm-devel \
    xcb-util-image-devel \
    freetype-devel \
    fontconfig-devel \
    libxml2-devel \
    alsa-lib-devel \
    SDL2-devel \
    speex-devel \
    libwebp-devel \
    zimg-devel \
    rubberband-devel \
    xcb-proto \
    xcb-util \
    xcb-util-keysyms \
    xcb-util-renderutil

cd "$SOURCE_DIR"

# Build and install libaom (AV1) if not already compiled
if ! is_locked "libaom"; then
    echo ">>> Building and installing libaom (AV1)..."
    git clone https://aomedia.googlesource.com/aom "$SOURCE_DIR/aom"
    mkdir -p "$SOURCE_DIR/aom_build"
    cd "$SOURCE_DIR/aom_build"
    cmake ../aom -DCMAKE_INSTALL_PREFIX="$BUILD_DIR" -DENABLE_SHARED=off
    make -j$(nproc)
    make install
    create_lock "libaom"
    cd ../..
else
    echo ">>> libaom (AV1) already compiled. Skipping..."
fi

# Build and install libsoxr if not already compiled
if ! is_locked "libsoxr"; then
    echo ">>> Building and installing libsoxr..."
    git clone https://git.code.sf.net/p/soxr/code "$SOURCE_DIR/soxr"
    mkdir -p "$SOURCE_DIR/soxr/build"
    cd "$SOURCE_DIR/soxr/build"
    cmake .. -DCMAKE_INSTALL_PREFIX="$BUILD_DIR" -DBUILD_SHARED_LIBS=OFF
    make -j$(nproc)
    make install
    create_lock "libsoxr"
    cd ../..
else
    echo ">>> libsoxr already compiled. Skipping..."
fi

# Build and install libvpx if not already compiled
if ! is_locked "libvpx"; then
    echo ">>> Building and installing libvpx..."
    git clone https://chromium.googlesource.com/webm/libvpx "$SOURCE_DIR/libvpx"
    cd "$SOURCE_DIR/libvpx"
    ./configure --prefix="$BUILD_DIR" --disable-examples --disable-unit-tests
    make -j$(nproc)
    make install
    create_lock "libvpx"
    cd ..
else
    echo ">>> libvpx already compiled. Skipping..."
fi

# Build and install SVT-AV1 if not already compiled
if ! is_locked "SVT-AV1"; then
    echo ">>> Building and installing SVT-AV1..."
    git clone https://gitlab.com/AOMediaCodec/SVT-AV1.git "$SOURCE_DIR/SVT-AV1"
    mkdir -p "$SOURCE_DIR/SVT-AV1/build"
    cd "$SOURCE_DIR/SVT-AV1/build"
    cmake .. -DCMAKE_INSTALL_PREFIX="$BUILD_DIR" -DBUILD_SHARED_LIBS=OFF
    make -j$(nproc)
    make install
    create_lock "SVT-AV1"
    cd ../..
else
    echo ">>> SVT-AV1 already compiled. Skipping..."
fi

# Clone the FFmpeg source if not already cloned
if [ ! -d "$SOURCE_DIR/ffmpeg" ]; then
    cd "$SOURCE_DIR"

    # Download FFmpeg source snapshot
    curl -O -L https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
    tar xjvf ffmpeg-snapshot.tar.bz2
fi

# Configure, build, and install FFmpeg if not already compiled
if ! is_locked "ffmpeg"; then
    echo ">>> Configuring FFmpeg build..."
    cd "$SOURCE_DIR/ffmpeg"
    PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
        --prefix="$BUILD_DIR" \
        --pkg-config-flags="--static" \
        --extra-cflags="-I$BUILD_DIR/include" \
        --extra-ldflags="-L$BUILD_DIR/lib" \
        --extra-libs="-lpthread -lm" \
        --bindir="$HOME/bin" \
        --enable-gpl \
        --enable-version3 \
        --enable-static \
        --disable-debug \
        --disable-shared \
        --enable-libx264 \
        --enable-libx265 \
        --enable-libfdk_aac \
        --enable-libmp3lame \
        --enable-libopus \
        --enable-libvpx \
        --enable-libaom \
        --enable-libass \
        --enable-libtheora \
        --enable-libvorbis \
        --enable-libvmaf \
        --enable-libbluray \
        --enable-libsoxr \
        --enable-libsvtav1 \
        --enable-librsvg \
        --enable-libfribidi \
        --enable-libmfx \
        --enable-libspeex \
        --enable-libwebp \
        --enable-libzimg \
        --enable-librubberband \
        --enable-gnutls \
        --enable-libfreetype \
        --enable-libfontconfig \
        --enable-libxml2 \
        --enable-alsa \
        --enable-libxcb \
        --enable-libxcb-shm \
        --enable-libxcb-xfixes \
        --enable-nonfree
    echo ">>> Building and installing FFmpeg..."
    make -j$(nproc)
    make install
    create_lock "ffmpeg"
    echo ">>> FFmpeg has been built and installed successfully."
else
    echo ">>> FFmpeg already compiled. Skipping..."
fi

# Execute the ffmpeg binary
echo ">>> Executing ffmpeg binary..."
~/bin/ffmpeg
