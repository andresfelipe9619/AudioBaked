# 🎧 AudioBaked

> Transcribe, analyze, and subtitle your audio & video files with speaker diarization, directly from the command line.

**AudioBaked** is a powerful and flexible Python tool for automated transcription and intelligent analysis of your media files. It leverages the cutting-edge accuracy of [WhisperX](https://github.com/m-bain/whisperX) to generate speaker-separated transcripts and can optionally use OpenAI's GPT models to provide insightful, structured analysis.

With its modular CLI interface, you can choose to extract audio, burn subtitles, export transcripts, or run a detailed business analysis with simple flags.

---

## ✨ Features

- **🎙️ Broad File Support:** Works seamlessly with `.mp4`, `.mov`, `.mp3`, and other common audio/video formats.
- **🗣️ Speaker Diarization:** Uses WhisperX to identify and label different speakers in the transcript (e.g., `SPEAKER_01`, `SPEAKER_02`).
- **🎧 Audio Extraction:** Includes a new `--extract-audio` flag to pull the audio from a video file into a separate `.mp3` for faster processing.
- **🤖 High-Quality Transcription:** Utilizes WhisperX for accurate speech-to-text conversion.
- **🧠 Advanced Business Analysis:** When using the `--analyze` flag, the transcript is sent to a GPT model with a specialized prompt to extract:
    - **General Notes & Summaries**
    - **Action Items**
    - **A Freelancer's To-Do List**
    - **Estimated Time & Budget**
- **📄 Analyze Existing Transcripts:** You can analyze any existing `.txt` file using the `--analyze-transcript` flag.
- **🎬 Multiple Output Modes:**
    - **`--burn`**: Burn subtitles directly into your original video file using `ffmpeg`.
    - **`--export-only`**: Save `.srt` and `.txt` transcript files without creating a new video.
- **⚙️ Flexible & Controllable:**
    - **`--model`**: Select the Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) to balance speed and accuracy.
    - **`--output-dir`**: Specify a custom directory for all output files. Subdirectories are created per file.

---

## 🧱 Requirements

- Python 3.9 or higher
- `ffmpeg` installed and available in your system's PATH
- An OpenAI API key (only required for the `--analyze` feature)
- A Hugging Face User Access Token (for speaker diarization)

---

## 🔧 Installation

**1. Clone the Repository**

First, clone this repository to your local machine and navigate into the directory.

```bash
git clone https://github.com/yourusername/audiobaked.git
cd audiobaked
```

**2. Set Up a Virtual Environment (Recommended)**

Using a virtual environment prevents conflicts with other Python projects.

* **macOS/Linux:**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

* **Windows:**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

**3. Install Dependencies**

Install the required Python libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

Alternatively, you can install the packages manually:

```bash
pip install openai python-dotenv rich torch whisperx
```

---

## ⚙️ Configuration

**🔐 Environment Variables**

To use the analysis and diarization features, you must set your API keys as environment variables.

Create a `.env` file in the project's root directory and add your keys:

```
OPENAI_API_KEY="sk-xxxxxx..."
HF_TOKEN="your_hugging_face_token"
```

- **OpenAI:** Required for the `--analyze` feature.
- **Hugging Face:** Required for speaker diarization. You can get a token from [hf.co/settings/tokens](https://hf.co/settings/tokens). You will also need to accept the user conditions for the [pyannote/segmentation-3.0](https://hf.co/pyannote/segmentation-3.0) model.


You can also optionally override the system prompt used for GPT analysis:

```
OPENAI_SYSTEM_PROMPT="Your custom analysis instructions here."
```

Alternatively, you can export the variable directly in your terminal session before running the script:

```bash
export OPENAI_API_KEY="sk-xxxxxx..."
export HF_TOKEN="your_hugging_face_token"
```

---

## 🚀 Usage

AudioBaked is controlled via command-line flags, allowing you to specify exactly what tasks to perform.

### Command-Line Arguments

| Flag                   | Description                                                            | Default    |
|------------------------|------------------------------------------------------------------------|------------|
| `file`                 | (Required) Path to the input video or audio file.                      | N/A        |
| `--extract-audio`      | Extract audio from video to an `.mp3` before processing.               | Off        |
| `--burn`               | Burn subtitles into the video. (Ignored if `--extract-audio` is used). | Off        |
| `--export-only`        | Only export the transcript files (`.srt`, `.txt`).                     | Off        |
| `--analyze`            | Send transcript to OpenAI for detailed business analysis.              | Off        |
| `--model`              | The Whisper model to use (`tiny`, `base`, `small`, `medium`, `large`). | `medium`   |
| `--output-dir`         | The directory where output files will be saved.                        | `./output` |
| `--analyze-transcript` | Analyze a `.txt` transcript file directly (skips transcription step).  | Off        |

### Examples

**1. Transcribe a video and burn subtitles:**

```bash
python main.py my_video.mp4 --burn
```

**2. Extract audio from a video, then generate transcripts and a business analysis:**

```bash
python main.py my_client_call.mp4 --extract-audio --analyze
```

**3. Export transcript files for an audio podcast (no video output):**

```bash
python main.py my_podcast.mp3 --export-only
```

**4. Do everything: burn subtitles and get an analysis from a video file:**

```bash
python main.py my_presentation.mov --burn --analyze
```

**5. Use a smaller model for speed and save to a specific folder:**

```bash
python main.py my_clip.mp4 --export-only --model small --output-dir ./exports
```

**6. Analyze an existing transcript file only (no media processing):**

```bash
python main.py dummy --analyze-transcript ./transcripts/meeting_notes.txt
```

### 🧾 Output Files

Based on the flags you use, the following files may be created inside an output subfolder:

- `yourfile.mp3`: The extracted audio file (created with `--extract-audio`).
- `yourfile.srt`: A standard subtitle file with speaker labels.
- `yourfile.txt`: A plain text version of the transcript with speaker labels.
- `yourfile_subtitled.mp4`: The final video with burned-in subtitles (created with `--burn`).
- `yourfile_analysis.md`: Markdown report from GPT (created with `--analyze`).

---

## 📦 Project Structure

```
audiobaked/
├── main.py                    # Main executable script
├── requirements.txt           # Python package dependencies
└── README.md                  # You are here
```

---

## 💡 Tips & Notes

- **GPU Acceleration:** For significantly faster processing, ensure you have a CUDA-compatible GPU and the necessary drivers installed. This will enable GPU acceleration for WhisperX.
- **Processing Time:** Transcribing long videos can be time-consuming, especially with larger models. Using `--extract-audio` can speed up this step.
- **Windows Paths:** If you encounter issues with file paths on Windows, try enclosing the path in double quotes.

---

## 💬 Future Ideas

- [x] Implement transcript chunking for deeper GPT analysis of long files.
- [x] Provide an option to save the GPT analysis to a Markdown file.
- [x] Add `--analyze-transcript` to analyze existing files.
- [ ] Develop a simple web UI for easy drag-and-drop functionality.
- [ ] Add a command-line flag to specify the transcription language.

---

## 🧙 About the Name

**AudioBaked**: Because your audio gets processed, toasted, analyzed, and served—ready to go. ✌️

---

## 📜 License

This project is licensed under the MIT License. Feel free to fork, bake, and remix it.
