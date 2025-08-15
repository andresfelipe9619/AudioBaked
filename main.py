import os
import sys
import argparse
import subprocess
import whisper
import openai

# === ENVIRONMENT CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def transcribe(file_path, model_size):
    print(f"🎤 Transcribing with Whisper ({model_size})...")
    model = whisper.load_model(model_size)
    result = model.transcribe(file_path, fp16=False)

    basename = os.path.splitext(os.path.basename(file_path))[0]
    srt_path = f"{basename}.srt"
    txt_path = f"{basename}.txt"

    with open(srt_path, "w", encoding="utf-8") as srt_file, open(txt_path, "w", encoding="utf-8") as txt_file:
        for i, segment in enumerate(result['segments']):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            srt_file.write(f"{i + 1}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")
            txt_file.write(f"{text}\n")

    print(f"✅ Transcript saved to {srt_path} and {txt_path}")
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
    if output_dir:
        output_path = os.path.join(output_dir, output_file)
    else:
        output_path = output_file

    print("🔥 Burning subtitles with ffmpeg...")
    subprocess.run([
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",
        output_path
    ], check=True)

    print(f"🎬 Final video: {output_path}")
    return output_path


def analyze_transcript(text):
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not set. Skipping analysis.")
        return

    print("🤖 Sending transcript to OpenAI for analysis...")
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
    print("🧠 Analysis:")
    print(response.choices[0].message.content)


def main():
    parser = argparse.ArgumentParser(description="🍃 AudioBaked: Transcribe, burn, and analyze audio & video files.")

    parser.add_argument("file", help="Path to the video or audio file")
    parser.add_argument("--burn", action="store_true", help="Burn subtitles into the video")
    parser.add_argument("--export-only", action="store_true", help="Only export the transcript (.srt and .txt)")
    parser.add_argument("--analyze", action="store_true", help="Send transcript to OpenAI for analysis")
    parser.add_argument("--model", default="medium", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("--output-dir", default=".", help="Directory for output files")

    args = parser.parse_args()

    srt_path, txt_path, transcript = transcribe(args.file, args.model)

    if args.export_only:
        print("🗃️ Export-only mode enabled. Skipping video rendering.")
    elif args.burn:
        burn_subtitles(args.file, srt_path, args.output_dir)

    if args.analyze:
        analyze_transcript(transcript)


if __name__ == "__main__":
    main()
