# Audio Transcriber Copilot Instructions

## Project Overview

This is a **Streamlit-based audio transcription web application** that converts `.wav` and `.mp3` audio files to text using multiple transcription backends. The project provides three different implementations to explore various transcription approaches.

**Key Technologies:** Streamlit (UI), Python, FFmpeg (audio processing), Whisper/SpeechRecognition/OpenAI APIs (transcription)

## Architecture & Component Strategy

### Three App Implementations (Experiment Pattern)

The codebase uses an **experimental pattern** with three parallel implementations exploring different transcription backends:

- **app.py** – OpenAI Whisper (`whisper` library, offline, multilingual support including Urdu)
- **app2.py** – Google Web Speech API via `speech_recognition` library (online, free, 60-second chunking)
- **app3.py** – OpenAI API (`openai` library, cloud-based, highest accuracy but requires API key)

**Important:** Only one app should be deployed at a time. Choose based on:
- **Whisper (app.py)**: Recommended for privacy, offline processing, Urdu support
- **Google API (app2.py)**: Recommended for simplicity, no API keys needed
- **OpenAI API (app3.py)**: Recommended for production accuracy, requires paid API key

### Shared Workflow Across All Apps

```
Upload Audio (WAV/MP3)
    ↓
[MP3] → FFmpeg Conversion → WAV
    ↓
Audio Transcription (backend-specific)
    ↓
Store in Streamlit Session State
    ↓
Display Preview + Download Button
    ↓
Cleanup Temp Files
```

### Audio Processing Pipeline

1. **File Upload**: Accepts WAV or MP3 via `st.file_uploader(accept_multiple_files=True)`
2. **Format Conversion**: MP3→WAV using `pydub` + FFmpeg (required for all backends)
3. **FFmpeg Detection**: `ensure_ffmpeg_available()` checks system PATH; fails gracefully if missing
4. **Transcription**: Backend-specific (offline Whisper vs. online APIs)
5. **Session Management**: Stores transcripts in `st.session_state` to persist across reruns
6. **Cleanup**: Removes temp files from `temp_audio/` directory after processing

### Critical Dependencies & Requirements

- **FFmpeg** (system dependency, not pip-installable)
  - Windows: `winget install Gyan.FFmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Must be in system PATH; `pydub` discovers it via `which("ffmpeg")`
- **Streamlit** – Web framework & session state management
- **pydub** – Audio format conversion (requires FFmpeg binary)
- **whisper** (app.py) OR **SpeechRecognition** (app2.py) OR **openai** (app3.py)

## Developer Workflows

### Running Locally

```bash
# Install dependencies
pip install -r requirement.txt

# Run Streamlit app (choose one)
streamlit run app.py      # Whisper backend
streamlit run app2.py     # Google Web Speech API
streamlit run app3.py     # OpenAI API
```

Default runs at `http://localhost:8501`

### Deployment (Systemd Service)

See [deploy.sh](deploy.sh) for production setup:

```bash
# Creates systemd service that:
# - Runs app.py as ubuntu user
# - Listens on 0.0.0.0:8503 (headless mode)
# - Max upload: 200MB
# - Auto-restarts on failure
sudo bash deploy.sh
sudo systemctl status audio-transcriber
```

### Testing Transcription Locally

1. Prepare test audio: `.wav` or `.mp3` file with clear speech
2. Upload via web UI or modify app temporarily to use `st.file_uploader()` with local path
3. Select language (Urdu for app.py, English for app2.py)
4. Click "Process" and monitor console for errors (FFmpeg issues, API failures)

## Project Patterns & Conventions

### Session State Pattern (Streamlit-Specific)

All transcripts are stored in `st.session_state.transcripts` as dict:

```python
st.session_state.transcripts = {
    "0_audio.mp3": {"name": "audio.mp3", "text": "transcribed text..."},
    "1_speech.wav": {"name": "speech.wav", "text": "..."}
}
```

**Why:** Streamlit reruns the entire script on every interaction; session state persists data across reruns without database overhead.

Temp file paths tracked separately in `st.session_state.temp_paths` for cleanup.

### Language Support Convention

- **app.py (Whisper)**: Maps language names to Whisper codes (`"urdu"→"ur"`, `"english"→"en"`)
- **app2.py (Google API)**: Hardcoded to English (`'en-US'`), with fallback to default
- **app3.py**: Uses OpenAI model directly (language auto-detected)

When adding language support, update the `language_map` dict in the respective app.

### Error Handling Pattern

All transcription functions return error messages as strings (not raising exceptions):

```python
def transcribe_audio(...):
    try:
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"  # Returns error as transcript string
```

**Why:** Streamlit UI displays all text uniformly in `st.text_area()`. Errors surface to users without app crashes.

### Temporary File Lifecycle

- **Creation**: `os.path.join(TEMP_DIR, f"{base_name}_{unique_id}.wav")`
- **Storage**: Path tracked in `st.session_state.temp_paths`
- **Cleanup**: Automatically removed after processing completes AND after download button clicked
- **Unique IDs**: Uses `uuid.uuid4().hex[:8]` to avoid collisions with concurrent users

## Integration Points & External Services

### FFmpeg Integration

- Discovered via `pydub.utils.which("ffmpeg")` at runtime
- Failures show user-friendly error message with install instructions
- Configured paths set directly on `AudioSegment` object

### Transcription Backends

| Backend | API Type | Language Support | Cost | Offline |
|---------|----------|------------------|------|---------|
| **Whisper** | Local model | 99 languages (incl. Urdu) | Free | Yes |
| **Google Web Speech** | HTTP API | Limited to selected langs | Free | No |
| **OpenAI API** | HTTP API | Auto-detected | Paid ($) | No |

For Whisper model sizes: tiny/base/small (fast, lower accuracy) → medium/large (slower, higher accuracy). Currently uses `"small"`.

## Key Files Reference

- [app.py](app.py) – Main Whisper-based implementation (recommended)
- [app2.py](app2.py) – Google Web Speech API alternative
- [app3.py](app3.py) – OpenAI API prototype (incomplete, has exposed API key)
- [deploy.sh](deploy.sh) – Systemd service configuration for Ubuntu
- [README.md](README.md) – User-facing installation & usage guide

## Enhancement Opportunities

### Common Improvements to Implement

1. **Multi-file parallelization**: Current implementation transcribes sequentially; could use threading for concurrent uploads
2. **Progress tracking**: Add progress bar for long transcriptions (`st.progress()`)
3. **Cached Whisper models**: Pre-download models to avoid first-run delay
4. **Export formats**: Add support for PDF/DOCX beyond plain text
5. **Batch processing**: Accept ZIP files with multiple audios
6. **API key management**: Move OpenAI key to environment variables (currently hardcoded in app3.py)

### Code Quality Notes

- No unit tests exist; focus on integration testing via web UI
- No logging system; errors only surface in Streamlit error UI
- Session state dict keys use format `"{index}_{filename}"` (fragile with special characters)
