#!/usr/bin/env bash
# Reconstruit toute la vidéo : voix off -> animation -> bande-son -> MP4 finaux.
# Prérequis : node + playwright (Chromium), python3 + numpy + soundfile + sherpa-onnx, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build output

python3 voice.py                                               # build/voice.wav + build/timeline.json
node render.js --fps=30 --out=build/video_silent.mp4           # build/cues.json
python3 audio.py build/cues.json build/voice.wav build/audio.wav
python3 audio.py build/cues.json build/voice.wav build/audio_voix_seule.wav --no-music

mux() {
  ffmpeg -hide_banner -loglevel error -y -i build/video_silent.mp4 -i "$1" -map 0:v -map 1:a \
    -c:v libx264 -preset slower -tune animation -crf 20 -maxrate 3M -bufsize 6M -profile:v high -level 4.0 -pix_fmt yuv420p \
    -c:a aac -b:a 160k -ar 48000 -movflags +faststart -shortest "$2"
}
mux build/audio.wav output/Seomastertech_SEO_explique.mp4
ffmpeg -hide_banner -loglevel error -y -i output/Seomastertech_SEO_explique.mp4 -i build/audio_voix_seule.wav -map 0:v -map 1:a -c:v copy \
  -af "volume=-1.2dB" -c:a aac -b:a 160k -ar 48000 -movflags +faststart -shortest output/Seomastertech_SEO_explique_sans_musique.mp4
echo "done -> output/"
