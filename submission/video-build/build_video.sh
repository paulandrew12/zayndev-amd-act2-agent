#!/usr/bin/env bash
# Assemble the Track 1 demo video: deck slides + real terminal captures + TTS narration.
set -euo pipefail
cd "$(dirname "$0")"
FONT=/System/Library/Fonts/Menlo.ttc
BG='#0d1117'; FG='#e6edf3'

render_text () {  # $1=infile $2=outfile $3=pointsize
  magick -background "$BG" -fill "$FG" -font "$FONT" -pointsize "$3" \
    label:@"$1" -bordercolor "$BG" -border 70 "$2"
}

# --- code snippet sources (from the repo, trimmed to fit a frame) ---
sed -n '35,51p' ../../agent/router.py   > code_router.txt
sed -n '12,21p' ../../agent/prompts.py  > code_prompts.txt
render_text code_router.txt   code_router.png   26
render_text code_prompts.txt  code_prompts.png  26
render_text eval_output.txt   term_eval.png     22
render_text container_output.txt term_container.png 24

# --- narration ---
i=0
narr () {
  i=$((i+1)); n=$(printf "%02d" $i)
  printf '%s' "$2" > "narr_$n.txt"
  say -v Samantha -r 182 -o "narr_$n.aiff" -f "narr_$n.txt"
  echo "$1" > "img_$n.txt"
}

narr slide-01.png "Track 1 is a token race. Pass the accuracy gate, then whoever answers on the fewest tokens wins. This is ZaynDev — a general-purpose agent engineered for exactly one number: total tokens. Built solo, from Nairobi."
narr slide-02.png "Everyone reaches for a fancy router to pick a cheaper model. But the token bill is not dominated by which model you pick. It is dominated by how much the model says."
narr slide-03.png "Left alone, these models think out loud before answering. That preamble wastes tokens on every task — and worse, it gets truncated by the token cap before the real answer arrives, so you fail the gate. Reasoning models are sneakier still: they can burn the entire token budget thinking, and return no answer at all."
narr slide-04.png "The design attacks verbosity in three stages. One: a zero token router. Pure regex sorts each task into one of eight categories — routing costs nothing, while an L L M based router pays for the classification and the answer. Two: the strongest allowed model per category, read live from the environment at runtime. Three: a terse, answer-only prompt per category — plus reasoning switched off at the A P I level."
narr code_router.png "Here is the entire router: a handful of compiled regexes. Ninety eight percent routing accuracy, at a cost of exactly zero tokens."
narr code_prompts.png "And the per category prompts. This is measured, not guessed — removing these lines drops accuracy and raises total tokens at the same time. Brevity instructions pay for themselves."
narr term_eval.png "I measure everything. Forty labelled tasks across all eight categories, with checkers that mirror the accuracy gate. On the real models: one hundred percent accuracy, run after run — and switching reasoning off cut total tokens by twenty nine percent, to about one hundred seventy tokens per task."
narr term_container.png "It ships exactly the way the judge runs it. The public image, pulled anonymously, reads tasks dot json and writes valid results dot json every time — eight out of eight. Per task model fallback means one flaky model never sinks the batch."
narr slide-07.png "The reference approach most teams will copy sends the raw prompt and lets the model ramble. Its fine tuned router literally ties with always picking the cheap model. The untapped lever is verbosity — and that is the one I pull hardest."
narr slide-08.png "It is a linux A M D sixty four container under two hundred megabytes. It starts in seconds, isolates every failure, and is M I T licensed in a public repo. Pass the gate. Spend the fewest tokens. That is ZaynDev."
narr slide-10.png "Repo and image on screen. Thank you."

# --- assemble segments ---
rm -f concat.txt
for n in $(seq -w 1 $i); do
  img=$(cat "img_$n.txt")
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "narr_$n.aiff")
  total=$(python3 -c "print(f'{float('$dur')+0.7:.2f}')")
  ffmpeg -y -loglevel error -loop 1 -framerate 30 -i "$img" -i "narr_$n.aiff" \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0d1117,format=yuv420p" \
    -t "$total" -c:v libx264 -preset fast -tune stillimage -c:a aac -b:a 128k -ar 44100 "seg_$n.mp4"
  echo "file 'seg_$n.mp4'" >> concat.txt
done
ffmpeg -y -loglevel error -f concat -safe 0 -i concat.txt -c copy ../ZaynDev-Track1-demo.mp4
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 ../ZaynDev-Track1-demo.mp4
