import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import os

#  Configuration
TEMP_AUDIO_FILE = "temp_audio.wav"

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

def convert_mp3_to_wav(uploaded_file):
    """
    Converts an uploaded MP3 file to WAV format using pydub.
    """
    try:
        if not ensure_ffmpeg_available():
            return False
        audio = AudioSegment.from_mp3(uploaded_file)
        # Export as wav
        audio.export(TEMP_AUDIO_FILE, format="wav")
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
    st.write("Upload a `.wav` or `.mp3` file to generate a text transcript.")

    # File Uploader supports both wav and mp3
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])

    if uploaded_file is not None:
        # Display audio player
        st.audio(uploaded_file)

        with st.spinner("Processing audio..."):
            
            success = False

            # Handle MP3 vs WAV
            if uploaded_file.name.endswith('.mp3'):
                # Convert MP3 to WAV first
                success = convert_mp3_to_wav(uploaded_file)
            else:
                # Save WAV directly
                with open(TEMP_AUDIO_FILE, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                success = True
            
            if success:
                # Perform Transcription
                transcript_text = transcribe_audio(TEMP_AUDIO_FILE)
                
                # Clean up temp file
                if os.path.exists(TEMP_AUDIO_FILE):
                    os.remove(TEMP_AUDIO_FILE)

                # Display Result
                st.success("Transcription Complete!")
                st.text_area("Preview:", value=transcript_text, height=300)

                # Generate TXT
                txt_data = save_to_txt(transcript_text)
                base_name = os.path.splitext(uploaded_file.name)[0] or "audio"
                suggested_name = f"{base_name}_transcript.txt"

                # Download Button
                st.download_button(
                    label="📄 Download Transcript as TXT",
                    data=txt_data,
                    file_name=suggested_name,
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()