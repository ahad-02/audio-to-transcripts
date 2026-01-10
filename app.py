import streamlit as st
import speech_recognition as sr
from fpdf import FPDF
from pydub import AudioSegment
import os

#  Configuration
TEMP_AUDIO_FILE = "temp_audio.wav"

#  Helper Functions

def convert_mp3_to_wav(uploaded_file):
    """
    Converts an uploaded MP3 file to WAV format using pydub.
    """
    try:
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

def save_to_pdf(text, filename="transcript.pdf"):
    """
    Saves the given text string into a PDF file.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add a title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Call Transcript", ln=True, align='C')
    pdf.ln(10)
    
    # Add the body text
    pdf.set_font("Arial", size=12)
    # encode to latin-1 to avoid unicode errors in basic fpdf
    # replace typically problematic characters
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# Main Application

def main():
    st.set_page_config(page_title="Audio to PDF Transcriber", layout="centered")
    
    st.title("🎙️ Audio to PDF Transcriber")
    st.write("Upload a `.wav` or `.mp3` file to generate a PDF transcript.")

    # File Uploader supports both wav and mp3
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])

    if uploaded_file is not None:
        # Display audio player
        st.audio(uploaded_file)
        
        if st.button("Transcribe & Generate PDF"):
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

                    # Generate PDF
                    pdf_data = save_to_pdf(transcript_text)

                    # Download Button
                    st.download_button(
                        label="📄 Download Transcript as PDF",
                        data=pdf_data,
                        file_name="call_transcript.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()