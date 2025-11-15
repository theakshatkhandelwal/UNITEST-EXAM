# PDF File Size Limits

## Current Limits

### 1. OCR.space API Limits

#### Free Tier (No API Key):
- **Maximum file size**: **10MB per PDF**
- **Rate limit**: 25,000 requests/month
- **Timeout**: 120 seconds per request

#### With API Key (Paid Plans):
- **Basic Plan**: Up to **20MB per PDF**
- **Pro Plan**: Up to **50MB per PDF**
- **Enterprise**: Custom limits (contact OCR.space)

### 2. Vercel Serverless Function Limits

- **Request body size**: **4.5MB** (hard limit for serverless functions)
- **Function timeout**: 
  - Hobby: 10 seconds
  - Pro: 60 seconds (default), up to 300 seconds (5 minutes) with config
  - Enterprise: Custom limits
- **Memory**: 1GB (default), up to 3GB with Pro plan

### 3. System Behavior

#### Files ≤ 10MB:
- ✅ Direct upload to OCR.space API
- ✅ Fastest processing
- ✅ Works with both free tier and API key

#### Files > 10MB (Free Tier):
- ⚠️ System attempts page-by-page processing
- ⚠️ May fail if pdf2image/Poppler not available (on Vercel)
- ⚠️ Falls back to base64 method (may be slower)

#### Files > 4.5MB (Vercel Limit):
- ❌ **Will fail** - Vercel serverless functions have a 4.5MB request body limit
- ❌ Cannot upload files larger than 4.5MB through Vercel

## Practical Limits

### Recommended Maximum:
- **4.5MB per PDF** (Vercel's hard limit)
- **10MB per PDF** if using OCR.space API with API key (but still limited by Vercel's 4.5MB)

### What Actually Works:

| File Size | Free Tier | With API Key | Notes |
|-----------|-----------|--------------|-------|
| < 4.5MB | ✅ Works | ✅ Works | Best experience |
| 4.5MB - 10MB | ❌ Vercel limit | ❌ Vercel limit | **Will fail** - Vercel blocks |
| > 10MB | ❌ Multiple limits | ❌ Multiple limits | **Will fail** |

## Important Notes

### Vercel's 4.5MB Limit is the Real Constraint

Even though OCR.space supports up to 10MB (free) or 50MB (paid), **Vercel's serverless functions have a 4.5MB request body limit**. This means:

- **Maximum upload size**: **4.5MB per PDF**
- Files larger than 4.5MB will be rejected by Vercel before reaching the OCR service
- This is a hard limit that cannot be bypassed

### Current Code Behavior

The code checks for 10MB (OCR.space limit) but the actual constraint is Vercel's 4.5MB:

```python
if file_size > 10 * 1024 * 1024:  # 10MB limit for free tier
    print(f"PDF file too large ({file_size} bytes). Will try page-by-page processing...")
```

**However**, Vercel will reject files > 4.5MB before this check runs.

## Solutions for Larger Files

### Option 1: Split Large PDFs (Recommended)
- Split PDFs into multiple files < 4.5MB each
- Upload multiple PDFs (system supports this)
- Each PDF processed independently

### Option 2: Upgrade Vercel Plan
- **Pro Plan**: Still 4.5MB limit for request body
- **Enterprise**: May have custom limits (contact Vercel)

### Option 3: Use Direct File Upload
- Upload files directly to cloud storage (S3, etc.)
- Process from storage (bypasses Vercel limit)
- Requires additional implementation

### Option 4: Client-Side Processing
- Process PDFs in browser before upload
- Extract text client-side
- Upload only text content
- Requires additional frontend implementation

## Recommendations

### For Best Results:
1. **Keep PDFs under 4.5MB** (Vercel limit)
2. **Use multiple PDFs** if content is large
3. **Compress PDFs** before upload if possible
4. **Use API key** for better reliability (even with smaller files)

### For Large Documents:
1. **Split into chapters/sections** (multiple PDFs)
2. **Compress images** in PDFs
3. **Remove unnecessary pages**
4. **Use text-based PDFs** when possible (smaller file size)

## File Size Optimization Tips

### Reduce PDF Size:
1. **Compress images** in PDF
2. **Remove embedded fonts** (if not needed)
3. **Use lower DPI** for scanned documents
4. **Remove metadata** and annotations
5. **Use PDF optimization tools**

### Tools for Compression:
- Adobe Acrobat (Optimize PDF)
- Online tools (SmallPDF, ILovePDF)
- Command line: `gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf`

## Summary

| Limit Type | Size | Applies To |
|------------|------|------------|
| **Vercel Request Body** | **4.5MB** | **Hard limit - cannot bypass** |
| OCR.space Free Tier | 10MB | Can be bypassed with API key |
| OCR.space Paid Tier | 20-50MB | Still limited by Vercel's 4.5MB |

**Bottom Line**: **Maximum supported PDF size is 4.5MB** due to Vercel's serverless function limits.

