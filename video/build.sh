#!/usr/bin/env bash
# Rebuilds the ad from scratch: frames -> silent video, soundtrack, final MP4s, cover and storyboard.
# Needs: node + playwright (Chromium), python3 + numpy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build output

node render.js --fps=30 --out=build/video_silent.mp4          # also writes build/cues.json
python3 audio.py build/cues.json build/audio.wav
python3 audio.py build/cues.json build/audio_sfx.wav --sfx-only

mux() {
  ffmpeg -hide_banner -loglevel error -y -i build/video_silent.mp4 -i "$1" -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$2"
}
mux build/audio.wav output/seomastertech_pub_9x16.mp4
mux build/audio_sfx.wav output/seomastertech_pub_9x16_sans_musique.mp4

# light copy for sharing (WhatsApp, Messenger, e-mail, Discord): ~5 MB, visually identical
ffmpeg -hide_banner -loglevel error -y -i build/video_silent.mp4 -i build/audio.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slower -tune animation -crf 21 -maxrate 2.6M -bufsize 5M -profile:v high -level 4.0 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 48000 -movflags +faststart -metadata title="Seomastertech – publicité" output/Seomastertech_pub.mp4

node render.js --stills=26.6
cp build/still_26.60.png output/seomastertech_cover.png
ffmpeg -hide_banner -loglevel error -y -i output/seomastertech_pub_9x16.mp4 \
  -vf "select='eq(n,45)+eq(n,99)+eq(n,150)+eq(n,213)+eq(n,265)+eq(n,345)+eq(n,385)+eq(n,462)+eq(n,515)+eq(n,580)+eq(n,676)+eq(n,750)+eq(n,792)+eq(n,825)',scale=270:480,tile=7x2:padding=6:color=white" \
  -frames:v 1 -vsync 0 output/storyboard.png
echo "done -> output/"
