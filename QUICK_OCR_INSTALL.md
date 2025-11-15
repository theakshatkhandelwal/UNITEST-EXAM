# ⚡ Quick OCR Installation Guide

## 🎯 What You Need

To enable OCR support for scanned/image-based PDFs, install:

1. **Python packages** (already in requirements.txt)
2. **Poppler** (for PDF to image conversion)
3. **Tesseract OCR** (the OCR engine)

## 📦 Quick Install Commands

### Windows:
```powershell
# 1. Install Python packages
pip install pdf2image Pillow pytesseract

# 2. Download and install Poppler:
#    https://github.com/oschwartz10612/poppler-windows/releases
#    Extract and add to PATH

# 3. Download and install Tesseract:
#    https://github.com/UB-Mannheim/tesseract/wiki
#    Install to default location (C:\Program Files\Tesseract-OCR)
```

### macOS:
```bash
# Install everything via Homebrew
brew install poppler tesseract
pip install pdf2image Pillow pytesseract
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
pip install pdf2image Pillow pytesseract
```

### Linux (Fedora):
```bash
sudo dnf install poppler-utils tesseract
pip install pdf2image Pillow pytesseract
```

## ✅ Test Installation

After installation, the system will automatically:
- ✅ Detect if OCR is available
- ✅ Use OCR when text extraction fails
- ✅ Show warnings if OCR is not available

## 🚀 How It Works

1. **Text-based PDFs**: Fast text extraction (no OCR needed)
2. **Scanned PDFs**: Automatic OCR fallback
3. **Mixed PDFs**: Combines both methods

## ⚠️ Important Notes

- **Serverless (Vercel)**: OCR may not work without custom build configuration
- **Performance**: OCR is slower (seconds per page)
- **Memory**: OCR uses more memory

## 📚 Full Guide

See `OCR_SETUP_GUIDE.md` for detailed instructions and troubleshooting.

