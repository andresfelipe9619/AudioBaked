import os
import argparse
import subprocess
import whisper
from openai import OpenAI

from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

# === RICH CONSOLE INITIALIZATION ===
console = Console()

# === ENVIRONMENT CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = os.getenv("OPENAI_SYSTEM_PROMPT", "You are a helpful assistant. Analyze the following transcript.")

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_audio(video_path, output_dir):
    basename = os.path.splitext(os.path.basename(video_path))[0]
    audio_path = os.path.join(output_dir, f"{basename}.mp3")

    console.print(f"🎧 [bold cyan]Extracting audio using ffmpeg...[/bold cyan]")
    subprocess.run([
        "ffmpeg",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        audio_path,
        "-y"
    ], check=True)

    console.print(f"✅ [bold green]Audio saved to:[/bold green] {audio_path}")
    return audio_path


def transcribe(file_path, model_size, output_dir):
    console.print(f"🎤 [bold cyan]Transcribing with Whisper ({model_size})...[/bold cyan]")
    model = whisper.load_model(model_size)
    result = model.transcribe(file_path, fp16=False)

    basename = os.path.splitext(os.path.basename(file_path))[0]
    srt_path = os.path.join(output_dir, f"{basename}.srt")
    txt_path = os.path.join(output_dir, f"{basename}.txt")

    with open(srt_path, "w", encoding="utf-8") as srt_file, open(txt_path, "w", encoding="utf-8") as txt_file:
        for i, segment in enumerate(result['segments']):
            start, end, text = segment['start'], segment['end'], segment['text'].strip()
            srt_file.write(f"{i + 1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")
            txt_file.write(f"{text}\n")

    console.print(f"✅ [bold green]Transcript saved to {srt_path} and {txt_path}[/bold green]")
    return srt_path, txt_path, result['text'], basename


def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


def burn_subtitles(video_path, srt_path, output_dir=None):
    basename = os.path.splitext(os.path.basename(video_path))[0]
    output_file = f"{basename}_subtitled.mp4"
    output_path = os.path.join(output_dir, output_file) if output_dir else output_file

    console.print("🔥 [bold orange3]Burning subtitles with ffmpeg...[/bold orange3]")
    subprocess.run([
        "ffmpeg", "-i", video_path, "-vf", f"subtitles={srt_path}", "-c:a", "copy", output_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    console.print(f"🎬 [bold green]Final video:[/bold green] {output_path}")
    return output_path


def analyze_transcript(text, basename, output_dir):
    if not OPENAI_API_KEY:
        console.print("⚠️ [bold yellow]OPENAI_API_KEY not set. Skipping analysis.[/bold yellow]")
        return

    console.print("🤖 [bold cyan]Sending transcript to OpenAI for analysis...[/bold cyan]")

    response = client.chat.completions.create(model="gpt-4",
                                              messages=[
                                                  {"role": "system", "content": SYSTEM_PROMPT},
                                                  {"role": "user",
                                                   "content": f"Analyze this transcript:\n\n{text[:8000]}"}
                                              ])

    analysis = response.choices[0].message.content

    console.print("🧠 [bold magenta]Analysis Result:[/bold magenta]")
    console.print(f"[dim]{'-' * 40}[/dim]")
    console.print(analysis)
    console.print(f"[dim]{'-' * 40}[/dim]")

    # Save to markdown file
    report_path = os.path.join(output_dir, f"{basename}_analysis.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(analysis)

    console.print(f"💾 [bold green]Analysis saved to:[/bold green] {report_path}")


def main():
    parser = argparse.ArgumentParser(description="🍃 AudioBaked: Transcribe, burn, and analyze audio & video files.")

    parser.add_argument("file", help="Path to the video or audio file")
    parser.add_argument("--extract-audio", action="store_true", help="Extract audio from video before processing")
    parser.add_argument("--burn", action="store_true", help="Burn subtitles into the video")
    parser.add_argument("--export-only", action="store_true", help="Only export the transcript (.srt and .txt)")
    parser.add_argument("--analyze", action="store_true", help="Send transcript to OpenAI for analysis")
    parser.add_argument("--model", default="medium", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--output-dir", default="output", help="Directory for output files")
    parser.add_argument("--analyze-transcript", help="Path to an existing transcript (.txt) file to analyze directly")

    args = parser.parse_args()

    if args.analyze_transcript:
        if not os.path.isfile(args.analyze_transcript):
            console.print(f"❌ [red]File not found:[/red] {args.analyze_transcript}")
            return

        with open(args.analyze_transcript, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        basename = os.path.splitext(os.path.basename(args.analyze_transcript))[0]
        output_dir = os.path.dirname(args.analyze_transcript)
        analyze_transcript(transcript_text, basename, output_dir)
        return

    input_path = args.file

    # Create execution subfolder based on file name
    input_basename = os.path.splitext(os.path.basename(input_path))[0]
    execution_dir = os.path.join(args.output_dir, input_basename)
    os.makedirs(execution_dir, exist_ok=True)

    if args.extract_audio:
        input_path = extract_audio(input_path, execution_dir)

    srt_path, txt_path, transcript, basename = transcribe(input_path, args.model, execution_dir)

    if args.export_only:
        console.print("🗃️ [yellow]Export-only mode enabled. Skipping video rendering.[/yellow]")
    elif args.burn and not args.extract_audio:
        burn_subtitles(args.file, srt_path, execution_dir)

    if args.analyze:
        analyze_transcript(transcript, basename, execution_dir)


if __name__ == "__main__":
    main()
