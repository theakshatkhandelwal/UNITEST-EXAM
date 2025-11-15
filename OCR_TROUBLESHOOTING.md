# OCR Troubleshooting Guide

## Current Issue: OCR Still Failing After Adding API Key

If you're still getting "Could not extract content from PDF(s)" after adding the OCR API key, follow these steps:

## Step 1: Verify API Key is Set Correctly

1. **Check Vercel Environment Variables:**
   - Go to Vercel Dashboard → Your Project
   - Settings → Environment Variables
   - Verify `OCR_SPACE_API_KEY` exists and is correct
   - Make sure it's enabled for **Production** environment

2. **Redeploy After Adding Key:**
   - After adding/updating the environment variable, you MUST redeploy
   - Vercel → Deployments → Click "Redeploy" on latest deployment
   - Or push a new commit to trigger redeploy

## Step 2: Check Vercel Logs

The improved logging will show exactly what's happening:

1. **Access Logs:**
   - Vercel Dashboard → Your Project → **Deployments**
   - Click on latest deployment → **Functions** tab
   - Or use Vercel CLI: `vercel logs [deployment-url]`

2. **Look for These Log Messages:**
   ```
   Processing PDF with cloud OCR (file size: X bytes)
   Using OCR.space API key (length: XX)
   Uploading PDF to OCR.space API...
   OCR.space API response status: XXX
   OCR.space API response keys: [...]
   ```

3. **Common Log Patterns:**

   **✅ Success Pattern:**
   ```
   OCR.space API response status: 200
   Cloud OCR (PDF direct) extracted X characters
   ```

   **❌ API Key Not Found:**
   ```
   WARNING: OCR_SPACE_API_KEY not found in environment variables
   ```
   **Solution:** Add the key and redeploy

   **❌ Authentication Error:**
   ```
   OCR.space API: Authentication failed (check API key)
   Status: 401
   ```
   **Solution:** Verify API key is correct

   **❌ Rate Limit:**
   ```
   OCR.space API: Rate limit exceeded
   Status: 429
   ```
   **Solution:** Wait or upgrade OCR.space plan

   **❌ Bad Request:**
   ```
   OCR.space API: Bad request - check file format
   Status: 400
   ```
   **Solution:** PDF might be corrupted or unsupported format

   **❌ No Text Found:**
   ```
   OCR Exit Code: 1 (success) but no ParsedResults
   ```
   **Solution:** PDF might be blank, too low quality, or handwritten

## Step 3: Test API Key Directly

You can test if your API key works:

1. **Get a test PDF** (scanned/image-based)
2. **Use curl or Postman:**
   ```bash
   curl -X POST https://api.ocr.space/parse/pdf \
     -H "apikey: YOUR_API_KEY" \
     -F "file=@test.pdf" \
     -F "language=eng" \
     -F "OCREngine=2"
   ```

3. **Check Response:**
   - Should return JSON with `ParsedResults`
   - If you get 401, API key is wrong
   - If you get 429, rate limit reached

## Step 4: Common Issues & Solutions

### Issue 1: API Key Not Being Read
**Symptoms:** Logs show "WARNING: OCR_SPACE_API_KEY not found"
**Solution:**
- Verify variable name is exactly `OCR_SPACE_API_KEY` (case-sensitive)
- Make sure it's enabled for Production environment
- Redeploy after adding

### Issue 2: PDF Too Large
**Symptoms:** Timeout or error
**Solution:**
- Free tier limit: 10MB per PDF
- Split large PDFs or upgrade OCR.space plan

### Issue 3: PDF Format Not Supported
**Symptoms:** Status 400 or no text extracted
**Solution:**
- Try converting PDF to images first
- Use a different PDF format
- Check if PDF is corrupted

### Issue 4: Rate Limit Exceeded
**Symptoms:** Status 429
**Solution:**
- Free tier: 25,000 requests/month
- Wait or upgrade OCR.space plan
- Check OCR.space dashboard for usage

### Issue 5: Low Quality PDF
**Symptoms:** OCR succeeds but extracts very little text
**Solution:**
- PDF might be too low resolution
- Try higher quality scan
- Handwritten text may not work well

## Step 5: Alternative Solutions

If OCR.space continues to fail:

1. **Enter Topic Manually:**
   - The system allows manual topic entry
   - Questions will still be generated

2. **Use Text-Based PDFs:**
   - Text-based PDFs work without OCR
   - Convert scanned PDFs to text-based if possible

3. **Check OCR.space Status:**
   - Visit: https://status.ocr.space/
   - Verify service is operational

## Step 6: Get Detailed Error Information

The improved logging now shows:
- API key status (found/not found)
- Request details (file size, parameters)
- Response status codes
- Full error messages
- Response structure

**All of this is in Vercel logs** - check them to see exactly what's happening.

## Quick Checklist

- [ ] API key added to Vercel environment variables
- [ ] Variable name is exactly `OCR_SPACE_API_KEY`
- [ ] Enabled for Production environment
- [ ] App redeployed after adding key
- [ ] Checked Vercel logs for detailed error messages
- [ ] Tested API key directly (optional)
- [ ] PDF is under 10MB (free tier limit)
- [ ] PDF is a valid, readable format

## Next Steps

1. **Deploy the latest code** (with improved logging)
2. **Check Vercel logs** when uploading a PDF
3. **Share the log output** if you need further help
4. **Verify API key** is working with a direct test

The improved logging will show exactly what's happening and why OCR is failing.

