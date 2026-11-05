#!/usr/bin/env bash
# Clean and level a talking-head recording's voice to YouTube loudness (-14 LUFS, -1.5 dBTP).
# usage: process_voice.sh <source video or audio> <out.wav>
#
# Check channels first (astats per channel): OBS mics are often dual-mono, and a
# dead channel hides in a downmix. This chain takes channel 1 (c0); change the pan
# if the live channel is c1.
# Order matters: highpass -> light denoise -> gentle compression -> copy to stereo
# -> two-pass linear loudnorm. The stereo copy must come BEFORE loudnorm: copying
# mono to both channels after normalising adds +3 dB and lands at -11 LUFS.
set -euo pipefail
src="$1"; out="$2"
PRE="pan=mono|c0=c0,highpass=f=80,afftdn=nf=-30:nr=10,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=3,pan=stereo|c0=c0|c1=c0"
M=$(ffmpeg -v info -i "$src" -vn -af "$PRE,loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
set -- $(echo "$M" | python -c "import json,sys;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
ffmpeg -v error -y -i "$src" -vn -af "$PRE,loudnorm=I=-14:TP=-1.5:LRA=9:measured_I=$1:measured_TP=$2:measured_LRA=$3:measured_thresh=$4:offset=$5:linear=true" \
  -ar 48000 -c:a pcm_s16le "$out"
printf "%s: " "$(basename "$out")"
ffmpeg -v info -i "$out" -af "ebur128=peak=true" -f null - 2>&1 | grep -A14 Summary | grep -E " I:|Peak:" | tr -s ' ' | tr '\n' ' '; echo
