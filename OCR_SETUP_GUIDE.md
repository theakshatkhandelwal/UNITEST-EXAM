# 🔍 OCR Setup Guide - Support for Scanned/Image-Based PDFs

This guide explains how to set up OCR (Optical Character Recognition) support so that scanned PDFs (image-based) can also be processed.

## 📋 What is OCR?

OCR (Optical Character Recognition) allows the system to extract text from scanned PDFs or PDFs that contain images of text. This is different from regular PDFs that have selectable text.

## 🛠️ Required Packages

The following Python packages are needed:
- `pdf2image` - Converts PDF pages to images
- `Pillow` (PIL) - Image processing library
- `pytesseract` - Python wrapper for Tesseract OCR engine

## 📦 Installation Steps

### Step 1: Install Python Packages

The packages are already added to `requirements.txt`. Install them:

```bash
pip install pdf2image Pillow pytesseract
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Install Poppler (Required for pdf2image)

Poppler is required for `pdf2image` to convert PDF pages to images:

#### Windows:
1. Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to a folder (e.g., `C:\poppler`)
3. Add `C:\poppler\Library\bin` to your system PATH

#### macOS:
```bash
brew install poppler
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install poppler-utils
```

#### Linux (Fedora):
```bash
sudo dnf install poppler-utils
```

### Step 3: Install Tesseract OCR Engine

Tesseract is the actual OCR engine. You need to install it separately:

#### Windows:
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)
3. During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR`)
4. Add Tesseract to your PATH, or set the path in code (see below)

#### macOS:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### Linux (Fedora):
```bash
sudo dnf install tesseract
```

### Step 4: Configure Tesseract Path (if needed)

If Tesseract is not in your system PATH, you may need to set the path in the code. The code will try to auto-detect, but if it fails, you can set it manually.

## ✅ Verification

After installation, test if OCR works:

```python
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Test OCR
image = Image.open('test_image.png')
text = pytesseract.image_to_string(image)
print(text)
```

## 🚀 How It Works

### Automatic Fallback System

The system uses a smart fallback approach:

1. **First**: Tries to extract text directly from PDF (fast, works for text-based PDFs)
2. **If that fails or extracts very little text**: Automatically uses OCR (slower, works for scanned PDFs)
3. **If OCR is not available**: Shows a warning but continues with whatever text was extracted

### Processing Flow

```
PDF Upload
    ↓
Try Text Extraction (PyPDF2)
    ↓
    ├─→ Success & Good Content → Use Text ✅
    │
    └─→ Failed or Little Content → Try OCR
            ↓
        ├─→ OCR Available → Extract with OCR ✅
        │
        └─→ OCR Not Available → Use Available Text (or None) ⚠️
```

## 🔧 Configuration

### Setting Tesseract Path Manually

If Tesseract is not found automatically, add this to `app.py` after the imports:

```python
# Set Tesseract path (Windows example)
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### For Vercel/Serverless Deployment

**Important**: Vercel serverless functions have limitations:
- Tesseract binary needs to be included in the deployment
- This requires custom build configuration
- Consider using a cloud OCR service for production

**Alternative for Production**: Use Google Cloud Vision API or AWS Textract instead of local Tesseract.

## 📝 Current Implementation

The code automatically:
- ✅ Detects if OCR libraries are available
- ✅ Falls back to OCR when text extraction fails
- ✅ Handles errors gracefully
- ✅ Works with multiple PDFs
- ✅ Combines text and OCR results when both are available

## ⚠️ Limitations

1. **Performance**: OCR is slower than text extraction (can take seconds per page)
2. **Accuracy**: OCR accuracy depends on image quality
3. **Serverless**: May not work on Vercel without custom configuration
4. **Memory**: OCR uses more memory (converts PDF pages to images)

## 🎯 Best Practices

1. **For text-based PDFs**: No OCR needed - fast text extraction works
2. **For scanned PDFs**: OCR is automatically used as fallback
3. **For mixed PDFs**: System combines both methods
4. **For production**: Consider cloud OCR services for better reliability

## 🔍 Troubleshooting

### "OCR libraries not installed" warning
- Install: `pip install pdf2image Pillow pytesseract`
- Check imports in `app.py`

### "Tesseract not found" error
- Install Tesseract OCR engine (see Step 2 above)
- Set path manually if needed (see Configuration)

### OCR is slow
- This is normal - OCR takes time
- Consider processing fewer pages
- Use higher quality scans for better results

### OCR accuracy is poor
- Ensure PDF images are high quality (300 DPI recommended)
- Check if PDF is rotated or skewed
- Consider preprocessing images before OCR

## 📚 Additional Resources

- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- pdf2image docs: https://github.com/Belval/pdf2image
- pytesseract docs: https://github.com/madmaze/pytesseract

---

**Note**: OCR support is optional. The system works without it, but scanned PDFs won't be processed.

