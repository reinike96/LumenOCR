# LumenOCR 📚🤖

A powerful Streamlit-based application to transcribe scanned PDF books into editable Word or Text files using **MistralOCR** and **Gemini 3 Flash** via OpenRouter.

## Features
- **High-Accuracy OCR**: Uses MistralOCR's advanced engine through OpenRouter's file-parser plugin.
- **Support for Large Books**: Automatically chunks PDFs (e.g., 5 pages at a time) to handle 800+ page books without hitting API size limits.
- **Multimodal AI**: Leverages Google's Gemini 3 Flash for perfect transcription and formatting.
- **Export Options**: Download results as `.txt` or `.docx` (Microsoft Word).
- **Privacy Center**: Users provide their own OpenRouter API key.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/pdf-ai-converter.git
   cd pdf-ai-converter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage
1. Open the app in your browser (usually `http://localhost:8501`).
2. Enter your **OpenRouter API Key**.
3. Upload a scanned PDF.
4. Set the "Pages per chunk" (smaller numbers for heavier scans).
5. Click **Start OCR Conversion** and wait for the magic to happen!

## License
MIT
