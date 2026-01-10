import streamlit as st
import speech_recognition as sr
from fpdf import FPDF
import os

# Configure Streamlit app
TEMP_AUDIO_FILE = "temp_audio.wav"
st.title("Audio to Text Converter and PDF Generator")

# Helper function to convert audio to text
def transcribe_audio(audio_file):
    """
    Transcribes a .wav file to text using Google Web Speech API.
    """
    recognizer = sr.Recognizer()
    
    # Load audio file
    with sr.AudioFile(audio_file) as source:
        # Record the audio data
        audio_data = recognizer.record(source)
        
        try:
            # Transcribe using Google's free API
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
    # multi_cell handles text wrapping automatically
    pdf.multi_cell(0, 10, txt=text)
    
    # Save output
    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output


# --- Main Application ---

def main():
    st.set_page_config(page_title="Audio to PDF Transcriber", layout="centered")
    
    st.title("🎙️ Audio to PDF Transcriber")
    st.write("Upload a `.wav` file to generate a PDF transcript.")

    # File Uploader
    uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        
        if st.button("Transcribe & Generate PDF"):
            with st.spinner("Transcribing... This may take a moment."):
                
                # Save uploaded file temporarily for processing
                with open(TEMP_AUDIO_FILE, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
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