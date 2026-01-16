import streamlit as st
from openai import OpenAI
import os
import uuid
from dotenv import load_dotenv


#  Configuration
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TEMP_DIR = "temp_audio"

def transcribe_audio(audio_file):
    """
    Transcribes an audio file to text using OpenAI
      GPT-4O API.
    
    Args:
        audio_file: Path to the audio file (.wav, .mp3, etc.)
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Open audio file in binary mode
        with open(audio_file, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f
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
            os.makedirs(TEMP_DIR, exist_ok=True)
            st.session_state.transcripts = {}
            st.session_state.temp_paths = {}
            with st.spinner("Processing audio..."):
                for index, uploaded_file in enumerate(uploaded_files):
                    unique_id = uuid.uuid4().hex[:8]
                    base_name = os.path.splitext(uploaded_file.name)[0] or "audio"
                    file_ext = uploaded_file.name.split('.')[-1]
                    temp_audio_path = os.path.join(TEMP_DIR, f"{base_name}_{unique_id}.{file_ext}")
                    
                    # Save uploaded file temporarily
                    uploaded_file.seek(0)
                    with open(temp_audio_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Transcribe directly without conversion
                    transcript_text = transcribe_audio(temp_audio_path)

                    file_key = f"{index}_{uploaded_file.name}"
                    st.session_state.transcripts[file_key] = {
                        "name": uploaded_file.name,
                        "text": transcript_text
                    }
                    st.session_state.temp_paths[file_key] = temp_audio_path

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