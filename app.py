import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import os
import uuid

#  Configuration
TEMP_AUDIO_FILE = "temp_audio.wav"
TEMP_DIR = "temp_audio"

#  Helper Functions

def ensure_ffmpeg_available():
    """
    Ensure FFmpeg and ffprobe are available for pydub and configure their paths.
    """
    ffmpeg_path = which("ffmpeg")
    ffprobe_path = which("ffprobe")
    if not ffmpeg_path or not ffprobe_path:
        st.error(
            "FFmpeg is required to process MP3 files but was not found.\n\n"
            "Install it and try again:\n\n"
            "  sudo apt update && sudo apt install -y ffmpeg"
        )
        return False
    # Configure pydub to use discovered binaries
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    return True

def convert_mp3_to_wav(uploaded_file, target_wav_path):
    """
    Converts an uploaded MP3 file to WAV format using pydub.
    """
    try:
        if not ensure_ffmpeg_available():
            return False
        uploaded_file.seek(0)
        audio = AudioSegment.from_mp3(uploaded_file)
        # Export as wav
        audio.export(target_wav_path, format="wav")
        return True
    except Exception as e:
        st.error(f"Error converting MP3: {e}")
        return False

def transcribe_audio(audio_file):
    """
    Transcribes a .wav file to text using Google Web Speech API.
    """
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Error: Could not understand audio."
        except sr.RequestError as e:
            return f"Error: Could not request results; {e}"

def save_to_txt(text, filename="transcript.txt"):
    """
    Returns the transcript as plain text for download.
    """
    return text

# Main Application

def main():
    st.set_page_config(page_title="Audio to Text Transcriber", layout="centered")
    
    st.title("🎙️ Audio to Text Transcriber")
    st.write("Upload one or more `.wav` or `.mp3` files to generate text transcripts.")
    
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
            os.makedirs(TEMP_DIR, exist_ok=True)
            st.session_state.transcripts = {}
            st.session_state.temp_paths = {}
            with st.spinner("Processing audio..."):
                for index, uploaded_file in enumerate(uploaded_files):
                    success = False
                    unique_id = uuid.uuid4().hex[:8]
                    base_name = os.path.splitext(uploaded_file.name)[0] or "audio"
                    temp_wav_path = os.path.join(TEMP_DIR, f"{base_name}_{unique_id}.wav")

                    if uploaded_file.name.lower().endswith(".mp3"):
                        success = convert_mp3_to_wav(uploaded_file, temp_wav_path)
                    else:
                        uploaded_file.seek(0)
                        with open(temp_wav_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        success = True
                    
                    if success:
                        transcript_text = transcribe_audio(temp_wav_path)
                    else:
                        transcript_text = "Error: Failed to prepare audio for transcription."

                    file_key = f"{index}_{uploaded_file.name}"
                    st.session_state.transcripts[file_key] = {
                        "name": uploaded_file.name,
                        "text": transcript_text
                    }
                    st.session_state.temp_paths[file_key] = temp_wav_path

                # Remove all temp audio files after processing all files
                for path in list(st.session_state.temp_paths.values()):
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                        except Exception:
                            pass
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