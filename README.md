# 🎧 AudioBaked

> Transcribe, analyze, and subtitle your audio & video files directly from the command line.

**AudioBaked** is a powerful and flexible Python tool for automated transcription and intelligent analysis of your media files. It leverages the cutting-edge accuracy of [OpenAI's Whisper](https://github.com/openai/whisper) to generate transcripts and can optionally use OpenAI's GPT models to provide insightful analysis. With its new CLI interface, you can choose to burn subtitles, export transcripts, or run analysis with simple flags.

---

## ✨ Features

- **🎙️ Broad File Support:** Works seamlessly with `.mp4`, `.mov`, `.mp3`, and other common audio/video formats.
- **🤖 High-Quality Transcription:** Utilizes OpenAI Whisper for accurate speech-to-text conversion.
- **🧠 Intelligent Analysis:** Optionally sends transcripts to an OpenAI GPT model for summarization or key insight extraction.
- **🎬 Multiple Output Modes:**
    - **`--burn`**: Burn subtitles directly into your video using `ffmpeg`.
    - **`--export-only`**: Save `.srt` and `.txt` transcript files without creating a new video.
- **⚙️ Flexible & Controllable:**
    - **`--model`**: Select the Whisper model size (`tiny`, `base`, `small`, `medium`, `large`) to balance speed and accuracy.
    - **`--output-dir`**: Specify a custom directory for all output files.
- **🐍 Simple & Scriptable:** A straightforward Python script perfect for command-line use and automation.

---

## 🧱 Requirements

- Python 3.9 or higher
- `ffmpeg` installed and available in your system's PATH
- An OpenAI API key (only required for the `--analyze` feature)

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

*   **macOS/Linux:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

*   **Windows:**
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
pip install openai-whisper openai
```

---

## ⚙️ Configuration

**🔐 Environment Variables**

To use the `--analyze` feature, you must set your OpenAI API key as an environment variable.

Create a `.env` file in the project's root directory and add your key:
```
OPENAI_API_KEY="sk-xxxxxx..."
```

Alternatively, you can export the variable directly in your terminal session before running the script:
```bash
export OPENAI_API_KEY="sk-xxxxxx..."
```

---

## 🚀 Usage

AudioBaked is now controlled via command-line flags, allowing you to specify exactly what tasks to perform.

### Command-Line Arguments

| Flag           | Description                                                        | Default      |
| :------------- | :----------------------------------------------------------------- | :----------- |
| `file`         | (Required) Path to the input video or audio file.                  | N/A          |
| `--burn`       | Burn the generated subtitles into the video.                       | Off          |
| `--export-only`| Only export the transcript files (`.srt`, `.txt`).                 | Off          |
| `--analyze`    | Send the transcript to OpenAI's GPT for analysis.                  | Off          |
| `--model`      | The Whisper model to use (tiny, base, small, medium, large).       | `medium`     |
| `--output-dir` | The directory where output files will be saved.                    | Current dir `.` |

### Examples

**1. Transcribe a video and burn subtitles:**
```bash
python transcribe_and_analyze.py my_video.mp4 --burn
```

**2. Export transcript files for an audio podcast (no video output):**
```bash
python transcribe_and_analyze.py my_podcast.mp3 --export-only
```

**3. Transcribe and get a summary from OpenAI (no video output):**
```bash
python transcribe_and_analyze.py my_meeting.mp4 --analyze
```

**4. Do everything: burn subtitles and get an analysis:**
```bash
python transcribe_and_analyze.py my_presentation.mov --burn --analyze
```

**5. Use a smaller model for speed and save to a specific folder:**
```bash
python transcribe_and_analyze.py my_clip.mp4 --burn --model small --output-dir ./exports
```

### 🧾 Output Files

Based on the flags you use, the following files may be created:
-   `yourfile.srt`: A standard subtitle file.
-   `yourfile.txt`: A plain text version of the transcript.
-   `yourfile_subtitled.mp4`: The final video with burned-in subtitles (created with `--burn`).
-   Analysis from GPT will be printed directly to your terminal (created with `--analyze`).

---

## 📦 Project Structure

```
audiobaked/
├── transcribe_and_analyze.py   # Main executable script
├── requirements.txt            # Python package dependencies
└── README.md                   # You are here
```

---

## 💡 Tips & Notes

-   **GPU Acceleration:** For significantly faster processing, ensure you have CUDA installed to enable GPU acceleration for the Whisper models.
-   **Processing Time:** Transcribing long videos can be time-consuming, especially with larger models.
-   **Windows Paths:** If you encounter issues with file paths on Windows, try enclosing the path in double quotes.

---

## 💬 Future Ideas

-   [ ] Implement transcript chunking for deeper GPT analysis of long files.
-   [ ] Develop a simple web UI for easy drag-and-drop functionality.
-   [ ] Add a command-line flag to specify the transcription language.
-   [ ] Provide an option to save the GPT analysis to a file (e.g., JSON or TXT).

---

## 🧙 About the Name

**AudioBaked**: Because your audio gets processed, toasted, analyzed, and served—ready to go. ✌️

---

## 📜 License

This project is licensed under the MIT License. Feel free to fork, bake, and remix it.