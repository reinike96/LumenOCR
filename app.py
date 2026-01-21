import streamlit as st
import requests
import json
import base64
import os
from dotenv import load_dotenv
from docx import Document
from io import BytesIO
from pypdf import PdfReader, PdfWriter

# Load environment variables
load_dotenv()

# Configuration
MODEL_ID = "google/gemini-3-flash-preview"

st.set_page_config(page_title="PDF to Text (MistralOCR)", page_icon="📚", layout="centered")

# Custom CSS for premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    .stFileUploader {
        border: 1px dashed #444;
        padding: 20px;
        border-radius: 10px;
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(#FF4B4B, #FF9B9B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 PDF Book to Text Converter")
st.subheader("Powered by Gemini 3 Flash & MistralOCR")
st.markdown("---")

# User input for API Key
api_key_input = st.text_input("Enter your OpenRouter API Key", type="password", help="Your key is not stored and is only used for the current session.")

uploaded_file = st.file_uploader("Select your PDF book", type=['pdf'])

def create_word_file(text):
    doc = Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

if uploaded_file is not None:
    st.info(f"File uploaded: {uploaded_file.name}")
    
    # PDF Info
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    st.write(f"Total pages: {total_pages}")
    
    # Settings for chunking
    pages_per_chunk = st.number_input("Pages per chunk", min_value=1, max_value=50, value=5)
    
    if st.button("Start OCR Conversion"):
        if not api_key_input:
            st.error("Please enter your OpenRouter API Key first.")
        else:
            try:
                full_text = ""
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Reset file pointer for reading
                uploaded_file.seek(0)
                
                num_chunks = (total_pages + pages_per_chunk - 1) // pages_per_chunk
                
                for i in range(num_chunks):
                    start_page = i * pages_per_chunk
                    end_page = min(start_page + pages_per_chunk, total_pages)
                    
                    status_text.text(f"Processing pages {start_page + 1} to {end_page}...")
                    
                    # Extract chunk to a new PDF bytes
                    writer = PdfWriter()
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    chunk_io = BytesIO()
                    writer.write(chunk_io)
                    chunk_bytes = chunk_io.getvalue()
                    base64_pdf = base64.b64encode(chunk_bytes).decode('utf-8')
                    file_data_url = f"data:application/pdf;base64,{base64_pdf}"
                    
                    # OpenRouter API call
                    headers = {
                        "Authorization": f"Bearer {api_key_input}",
                        "HTTP-Referer": "https://github.com/antigravity",
                        "X-Title": "PDF Book Converter",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": MODEL_ID,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    { "type": "text", "text": f"Transcribe pages {start_page + 1} to {end_page} of this document completely and accurately. Output ONLY the transcribed text." },
                                    {
                                        "type": "file",
                                        "file": {
                                            "filename": f"pages_{start_page+1}_{end_page}.pdf",
                                            "file_data": file_data_url
                                        }
                                    }
                                ]
                            }
                        ],
                        "plugins": [
                            {
                                "id": "file-parser",
                                "pdf": {
                                    "engine": "mistral-ocr"
                                }
                            }
                        ],
                        "reasoning": { "exclude": True }
                    }
                    
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload),
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        chunk_text = result['choices'][0]['message']['content']
                        full_text += chunk_text + "\n\n"
                        progress_bar.progress((i + 1) / num_chunks)
                    else:
                        st.error(f"Error at chunk {i+1} (pages {start_page+1}-{end_page}): {response.status_code} - {response.text}")
                        break
                
                if full_text:
                    st.success("Conversion Complete!")
                    st.text_area("Preview (First 2000 characters)", full_text[:2000] + "...", height=300)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download as TXT",
                            data=full_text,
                            file_name=f"{os.path.splitext(uploaded_file.name)[0]}.txt",
                            mime="text/plain"
                        )
                    with col2:
                        word_bio = create_word_file(full_text)
                        st.download_button(
                            label="Download as Word",
                            data=word_bio,
                            file_name=f"{os.path.splitext(uploaded_file.name)[0]}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

st.markdown("---")
st.caption("Note: Large books are processed in chunks to ensure accuracy and stay within API limits.")
