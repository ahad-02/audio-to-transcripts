# Audio Transcriber with GPT-4O

A clean and simple Python web application that transcribes audio files (`.wav` and `.mp3`) into text using OpenAI's GPT-4O model. Built with **Streamlit**.

## 🚀 Features

* **Audio Support:** Accepts both `.wav` and `.mp3` files.
* **Automatic Conversion:** Automatically converts MP3s to WAV format for processing.
* **GPT-4O Transcription:** Uses OpenAI's advanced GPT-4O audio model for accurate transcription.
* **Multi-Language Support:** Automatically detects and transcribes multiple languages.
* **Batch Processing:** Upload and transcribe multiple files at once.
* **Text Download:** Download transcripts as plain text files.
* **Browser Interface:** Simple, drag-and-drop UI powered by Streamlit.

## 🛠️ Prerequisites

Before running the project, ensure you have the following installed:

* **Python 3.8+**
* **FFmpeg** (Required for MP3 processing)
    * *Windows:* `winget install Gyan.FFmpeg`
    * *Mac:* `brew install ffmpeg`
    * *Linux:* `sudo apt install ffmpeg`
* **OpenAI API Key** (Get one at https://platform.openai.com/api-keys)

## 📦 Installation

1. **Clone the repository** (or download the source code):
    ```bash
    git clone https://github.com/yourusername/audio-transcriber.git
    cd audio-transcriber
    ```

2. **Create a Virtual Environment** (Recommended):
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirement.txt
    ```

4. **Set up Environment Variables:**
    ```bash
    # Copy the example file
    cp .env.example .env
    
    # Edit .env and add your OpenAI API key
    # OPENAI_API_KEY=sk-your-api-key-here
    ```

## ▶️ Usage

1. **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

2. **Open your browser:**
    The app should open automatically at `http://localhost:8501`.

3. **Transcribe Audio:**
    * Upload one or more `.wav` or `.mp3` files.
    * The app will display audio players for preview.
    * Click **"Process"** to start transcription.
    * Wait for the process to complete.
    * Preview the transcription and download as a text file.

## 🔑 API Key Management

* Create a `.env` file in the project root directory
* Add your OpenAI API key: `OPENAI_API_KEY=sk-your-key-here`
* The app will load this automatically at startup
* Never commit the `.env` file to version control

## 📋 Project Structure

* `app.py` - Main Streamlit application using GPT-4O
* `app2.py` - Alternative implementation using Google Web Speech API
* `app3.py` - Alternative implementation using OpenAI API (prototype)
* `requirement.txt` - Python dependencies
* `.env.example` - Template for environment variables
* `deploy.sh` - Systemd service configuration for Linux deployment
* `temp_audio/` - Temporary directory for audio processing

## 🚀 Deployment

### Local Deployment
Simply run `streamlit run app.py` as described above.

### Production Deployment (Ubuntu/Linux)
See `deploy.sh` for systemd service setup:
```bash
sudo systemctl stop audio-transcriber
sudo systemctl disable --now audio-transcriber
sudo systemctl status audio-transcriber --no-pager
```

## 📝 Notes

* FFmpeg must be installed and accessible in your system PATH
* Temporary audio files are automatically cleaned up after processing
* GPT-4O model automatically detects the language of the audio
* Each OpenAI API call will incur charges based on your usage plan

## 📄 License

MIT License - feel free to use and modify this project.
