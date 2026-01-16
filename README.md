# Audio to PDF Transcriber

A clean and simple Python web application that transcribes audio files (`.wav` and `.mp3`) into text and generates a downloadable PDF transcript. Built with **Streamlit**.

## 🚀 Features

* **Audio Support:** Accepts both `.wav` and `.mp3` files.
* **Automatic Conversion:** Automatically converts MP3s to WAV format for processing.
* **Transcription:** Uses the Google Web Speech API for speech-to-text conversion.
* **PDF Generation:** Instantly downloads the transcription as a formatted PDF.
* **Browser Interface:** Simple, drag-and-drop UI powered by Streamlit.

## 🛠️ Prerequisites

Before running the project, ensure you have the following installed:

* **Python 3.8+**
* **FFmpeg** (Required for MP3 processing)
    * *Windows:* `winget install Gyan.FFmpeg`
    * *Mac:* `brew install ffmpeg`
    * *Linux:* `sudo apt install ffmpeg`
```
    sudo dpkg --configure -a
    sudo apt -f install
    sudo apt update
    sudo apt install -y ffmpeg
    which ffmpeg && ffprobe -version
```
## 📦 Installation

1.  **Clone the repository** (or download the source code):
    ```bash
    git clone [https://github.com/ahad-02/audio-to-pdf-transcriber.git](https://github.com/yourusername/audio-to-pdf-transcriber.git)
    cd audio-to-pdf-transcriber
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install streamlit fpdf pydub
    pip install -U openai-whisper
    ```

## ▶️ Usage

1.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

2.  **Open your browser:**
    The app should open automatically at `http://localhost:8501`.

3.  **Transcribe:**
    * Upload your `.wav` or `.mp3` file.
    * Click **"Transcribe & Generate PDF"**.
    * Wait for the process to finish and click **"Download Transcript as PDF"**.
