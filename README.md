# PDF/Word/PPT Watermarking App

A desktop application built with PyQt6 that allows users to upload PDF, Word (.docx), or PowerPoint (.pptx) files, add a custom watermark, and download the watermarked file in the same format.

## Features
- Upload PDF, Word, or PowerPoint files
- Add custom text watermark
- Download the watermarked file in the same format

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Setup
1. Clone the repository or download the source code.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage
1. Launch the app.
2. Click 'Upload' to select a PDF, Word, or PowerPoint file.
3. Enter your desired watermark text.
4. Click 'Add Watermark'.
5. Save the resulting file when prompted.

---

**Note:**
- Only .pdf, .docx, and .pptx files are supported.
- The watermark is applied as text to each page/slide. 