"""Batch transcription tuned for Latin American Spanish meetings.

Runs Whisper large-v3 on Apple Silicon via mlx-whisper (uses the GPU, unlike
WhisperX which is CPU-only on macOS). Writes a plain .txt and an .srt per input.

Domain vocabulary / register hints are project-specific and are NOT stored in
this repo. Provide them at runtime with one of:

    * env var  WHISPER_INITIAL_PROMPT  (e.g. in a local .env file)
    * CLI flag --initial-prompt "..."
    * CLI flag --initial-prompt-file path/to/prompt.txt

Usage:
    python transcribe_mlx.py <audio_or_video> [<more> ...] --output-dir output
"""
import argparse
import os

import mlx_whisper
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()

MODEL = "mlx-community/whisper-large-v3-mlx"

# Generic fallback. Seed real domain terms via WHISPER_INITIAL_PROMPT / --initial-prompt.
DEFAULT_INITIAL_PROMPT = (
    "Transcripción de una reunión de trabajo en español latinoamericano, "
    "con puntuación y acentos correctos."
)


def resolve_initial_prompt(args):
    if args.initial_prompt_file:
        with open(args.initial_prompt_file, encoding="utf-8") as f:
            return f.read().strip()
    if args.initial_prompt:
        return args.initial_prompt
    return os.getenv("WHISPER_INITIAL_PROMPT", DEFAULT_INITIAL_PROMPT)


def build_decode_kwargs(initial_prompt):
    return dict(
        language="es",
        task="transcribe",
        initial_prompt=initial_prompt,
        condition_on_previous_text=False,      # stops accent-driven repetition loops
        temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        no_speech_threshold=0.6,
        compression_ratio_threshold=2.4,
        logprob_threshold=-1.0,
        word_timestamps=False,
    )


def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


def transcribe(path, output_dir, decode_kwargs):
    basename = os.path.splitext(os.path.basename(path))[0]
    exec_dir = os.path.join(output_dir, basename)
    os.makedirs(exec_dir, exist_ok=True)

    console.print(f"🎤 [bold cyan]{basename}[/bold cyan] — large-v3 (mlx)...")
    result = mlx_whisper.transcribe(
        path, path_or_hf_repo=MODEL, verbose=False, **decode_kwargs
    )

    txt_path = os.path.join(exec_dir, f"{basename}.txt")
    srt_path = os.path.join(exec_dir, f"{basename}.srt")
    with open(txt_path, "w", encoding="utf-8") as txt, open(srt_path, "w", encoding="utf-8") as srt:
        for i, seg in enumerate(result["segments"], 1):
            text = seg["text"].strip()
            txt.write(text + "\n")
            srt.write(f"{i}\n{format_time(seg['start'])} --> {format_time(seg['end'])}\n{text}\n\n")

    console.print(f"✅ [green]{txt_path}[/green]")
    return txt_path


def main():
    parser = argparse.ArgumentParser(description="Latin American Spanish batch transcription (mlx-whisper large-v3)")
    parser.add_argument("files", nargs="+", help="audio or video files")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--initial-prompt", help="decoder seed prompt with domain vocabulary")
    parser.add_argument("--initial-prompt-file", help="file to read the seed prompt from")
    args = parser.parse_args()

    decode_kwargs = build_decode_kwargs(resolve_initial_prompt(args))

    for path in args.files:
        if not os.path.isfile(path):
            console.print(f"❌ [red]not found:[/red] {path}")
            continue
        transcribe(path, args.output_dir, decode_kwargs)


if __name__ == "__main__":
    main()
