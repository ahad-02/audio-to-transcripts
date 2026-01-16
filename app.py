import streamlit as st
from openai import OpenAI
import os
import uuid
from dotenv import load_dotenv
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


#  Configuration
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TEMP_DIR = "temp_audio"
MAX_TEMP_FILE_AGE_SECONDS = 600  # 10 minutes

_cleanup_thread = None
_cleanup_stop_event = threading.Event()

def delete_old_files_in_directory(directory: str, max_age_seconds: int) -> None:
    """
    Delete files older than max_age_seconds in directory. Ignores errors.
    """
    now = time.time()
    directory_path = Path(directory)
    if not directory_path.exists():
        return
    for path in directory_path.iterdir():
        try:
            if path.is_file():
                mtime = path.stat().st_mtime
                if now - mtime > max_age_seconds:
                    # Best-effort deletion; ignore races
                    path.unlink(missing_ok=True)
        except Exception:
            # Ignore deletion errors
            pass

def _cleanup_loop(directory: str, max_age_seconds: int, interval_seconds: int) -> None:
    while not _cleanup_stop_event.is_set():
        delete_old_files_in_directory(directory, max_age_seconds)
        # Sleep with interruptibility
        _cleanup_stop_event.wait(interval_seconds)

def ensure_cleanup_thread_running(
    directory: str,
    max_age_seconds: int = MAX_TEMP_FILE_AGE_SECONDS,
    interval_seconds: int = 600,
) -> None:
    """
    Start a daemon thread that periodically cleans up stale files.
    Safe to call multiple times; will only start one thread per process.
    """
    global _cleanup_thread
    Path(directory).mkdir(parents=True, exist_ok=True)
    if _cleanup_thread is None or not _cleanup_thread.is_alive():
        _cleanup_thread = threading.Thread(
            target=_cleanup_loop,
            args=(directory, max_age_seconds, interval_seconds),
            name="temp-audio-cleaner",
            daemon=True,
        )
        _cleanup_thread.start()

def transcribe_audio(audio_file):
    """
    Transcribes audio to text using OpenAI GPT-4o Transcribe.
    
    Args:
        audio_file: Path to the audio file (.wav, .mp3, etc.)
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Open audio file in binary mode using a proper file path (required by API)
        if not isinstance(audio_file, (str, os.PathLike)):
            return "Error: Internal - expected file path for transcription."
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f,
            )

        transcript_text = transcript.text.strip() if transcript.text else ""
        
        if transcript_text:
            return transcript_text
        else:
            return "Error: Could not understand audio. Try a file with clearer speech."
            
    except Exception as e:
        return f"Error: Failed to transcribe audio - {str(e)}"

def save_to_txt(text, filename="transcript.txt"):
    """
    Returns the transcript as plain text for download.
    """
    return text

# Main Application

def main():
    st.set_page_config(page_title="Audio to Text Transcriber", layout="centered")
    
    st.title("🎙️ Audio to Text Transcriber")
    st.write("Upload a `.wav` or `.mp3` file to generate a text transcript using GPT-4O.")

    # Ensure temp directory exists and clean stale files; start periodic cleaner
    ensure_cleanup_thread_running(TEMP_DIR)
    delete_old_files_in_directory(TEMP_DIR, MAX_TEMP_FILE_AGE_SECONDS)
    
    # Check if API key is loaded
    if not OPENAI_API_KEY:
        st.error("❌ OpenAI API key not found. Please add OPENAI_API_KEY to your .env file.")
        return
    
    if "transcripts" not in st.session_state:
        st.session_state.transcripts = {}
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "temp_paths" not in st.session_state:
        st.session_state.temp_paths = {}

    # File Uploader supports both wav and mp3; allow multiple files
    uploaded_files = st.file_uploader(
        "Choose one or more audio files",
        type=["wav", "mp3"],
        accept_multiple_files=True
    )

    if uploaded_files:
        # Display audio players
        for index, uploaded_file in enumerate(uploaded_files):
            st.audio(uploaded_file)

        def remove_transcript(key_to_remove: str):
            if key_to_remove in st.session_state.transcripts:
                del st.session_state.transcripts[key_to_remove]
            if key_to_remove in st.session_state.temp_paths:
                path = st.session_state.temp_paths.pop(key_to_remove)
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass

        if st.button("Process", key="process_button"):
            Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
            st.session_state.transcripts = {}
            st.session_state.temp_paths = {}
            with st.spinner("Processing audio..."):
                # Persist uploaded files to disk with proper extension for API compatibility
                files_to_process = []
                for uploaded_file in uploaded_files:
                    unique_id = uuid.uuid4().hex[:8]
                    base_name = os.path.splitext(uploaded_file.name)[0] or "audio"
                    file_ext = uploaded_file.name.split('.')[-1]
                    temp_audio_path = os.path.join(TEMP_DIR, f"{base_name}_{unique_id}.{file_ext}")
                    uploaded_file.seek(0)
                    with open(temp_audio_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    files_to_process.append((uploaded_file.name, temp_audio_path))

                max_workers = min(4, max(1, len(files_to_process)))
                futures = {}
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for name, path in files_to_process:
                        def task(p=path):
                            try:
                                return transcribe_audio(p)
                            finally:
                                # Best-effort delete to free disk space immediately after use
                                try:
                                    os.remove(p)
                                except Exception:
                                    pass
                        futures[executor.submit(task)] = name

                    for future in as_completed(futures):
                        name = futures[future]
                        unique_id = uuid.uuid4().hex[:8]
                        try:
                            transcript_text = future.result()
                        except Exception as e:
                            transcript_text = f"Error: Failed to transcribe audio - {str(e)}"
                        file_key = f"{unique_id}_{name}"
                        st.session_state.transcripts[file_key] = {
                            "name": name,
                            "text": transcript_text
                        }

                # Best-effort cleanup of any aged files left behind
                delete_old_files_in_directory(TEMP_DIR, MAX_TEMP_FILE_AGE_SECONDS)
                st.session_state.temp_paths = {}
                st.session_state.processed = True

        # Render results if present
        for file_key, data in list(st.session_state.transcripts.items()):
            transcript_text = data["text"]
            name = data["name"]
            st.success(f"Transcription Complete: {name}")
            st.text_area(
                f"Preview: {name}",
                value=transcript_text,
                height=200,
                key=f"preview_{file_key}"
            )

            txt_data = save_to_txt(transcript_text)
            base_name = os.path.splitext(name)[0] or "audio"
            suggested_name = f"{base_name}_transcript.txt"

            st.download_button(
                label=f"📄 Download Transcript for {name}",
                data=txt_data,
                file_name=suggested_name,
                mime="text/plain",
                key=f"download_{file_key}",
                on_click=remove_transcript,
                args=(file_key,)
            )

if __name__ == "__main__":
    main()