import os
import argparse
import subprocess
import whisper
import openai
from rich.console import Console

# === RICH CONSOLE INITIALIZATION ===
console = Console()

# === ENVIRONMENT CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


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
        "-y"  # overwrite without asking
    ], check=True)

    console.print(f"✅ [bold green]Audio saved to:[/bold green] {audio_path}")
    return audio_path


def transcribe(file_path, model_size):
    console.print(f"🎤 [bold cyan]Transcribing with Whisper ({model_size})...[/bold cyan]")
    model = whisper.load_model(model_size)
    result = model.transcribe(file_path, fp16=False)

    basename = os.path.splitext(os.path.basename(file_path))[0]
    srt_path = f"{basename}.srt"
    txt_path = f"{basename}.txt"

    with open(srt_path, "w", encoding="utf-8") as srt_file, open(txt_path, "w", encoding="utf-8") as txt_file:
        for i, segment in enumerate(result['segments']):
            start, end, text = segment['start'], segment['end'], segment['text'].strip()
            srt_file.write(f"{i + 1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")
            txt_file.write(f"{text}\n")

    console.print(f"✅ [bold green]Transcript saved to {srt_path} and {txt_path}[/bold green]")
    return srt_path, txt_path, result['text']


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
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Hide ffmpeg output

    console.print(f"🎬 [bold green]Final video:[/bold green] {output_path}")
    return output_path


def analyze_transcript(text):
    if not OPENAI_API_KEY:
        console.print("⚠️ [bold yellow]OPENAI_API_KEY not set. Skipping analysis.[/bold yellow]")
        return

    console.print("🤖 [bold cyan]Sending transcript to OpenAI for analysis...[/bold cyan]")
    openai.api_key = OPENAI_API_KEY

    system_prompt = """You are a top-tier business analyst and project manager. Your task is to analyze the following transcript and extract key information for a freelancer.

Please provide the following, based on the content of the conversation:

1.  **General Notes:** A summary of the key topics discussed, decisions made, and important information mentioned.
2.  **Action Items:** A clear list of tasks that need to be completed, with assigned owners if mentioned.
3.  **Freelancer's To-Do List:** A specific, actionable list of tasks for the freelancer based on the conversation.
4.  **Estimated Time & Budget:** A clever and realistic estimation of the time (in hours or days) and budget required for the project discussed. If not explicitly mentioned, provide a reasonable estimate based on the scope of work.

Format the output in Markdown.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this transcript:\n\n{text[:8000]}"}
        ]
    )

    console.print("🧠 [bold magenta]Analysis Result:[/bold magenta]")
    console.print(f"[dim]{'-' * 40}[/dim]")
    console.print(response.choices[0].message.content)
    console.print(f"[dim]{'-' * 40}[/dim]")


def main():
    parser = argparse.ArgumentParser(description="🍃 AudioBaked: Transcribe, burn, and analyze audio & video files.")

    parser.add_argument("file", help="Path to the video or audio file")
    parser.add_argument("--extract-audio", action="store_true", help="Extract audio from video before processing")
    parser.add_argument("--burn", action="store_true", help="Burn subtitles into the video")
    parser.add_argument("--export-only", action="store_true", help="Only export the transcript (.srt and .txt)")
    parser.add_argument("--analyze", action="store_true", help="Send transcript to OpenAI for analysis")
    parser.add_argument("--model", default="medium", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--output-dir", default=".", help="Directory for output files")

    args = parser.parse_args()

    input_path = args.file

    if args.extract_audio:
        input_path = extract_audio(args.file, args.output_dir)

    srt_path, txt_path, transcript = transcribe(input_path, args.model)

    if args.export_only:
        console.print("🗃️ [yellow]Export-only mode enabled. Skipping video rendering.[/yellow]")
    elif args.burn and not args.extract_audio:
        burn_subtitles(args.file, srt_path, args.output_dir)

    if args.analyze:
        analyze_transcript(transcript)


if __name__ == "__main__":
    main()
