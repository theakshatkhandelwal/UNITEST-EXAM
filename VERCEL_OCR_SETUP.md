# Vercel OCR Setup Guide

## Do I Need to Update Vercel?

**Short Answer: NO** - You don't need to install anything on Vercel. The cloud OCR API works without any system dependencies.

However, you may want to add an **optional API key** for better reliability and higher rate limits.

## Current Setup

The system uses **OCR.space API** which:
- ✅ Works in serverless environments (no Poppler/Tesseract needed)
- ✅ Free tier: 25,000 requests/month
- ✅ No Vercel configuration required

## Optional: Get OCR.space API Key (Recommended for Production)

### Why Get an API Key?
- Higher rate limits (unlimited for paid plans)
- Better reliability
- No rate limit errors
- Faster processing

### Steps to Get API Key:

1. **Sign up for OCR.space**
   - Visit: https://ocr.space/ocrapi
   - Click "Sign Up" or "Get API Key"
   - Create a free account

2. **Get Your API Key**
   - After signup, you'll receive an API key
   - Free tier: 25,000 requests/month
   - Paid plans available for higher limits

3. **Add to Vercel Environment Variables**
   - Go to your Vercel project dashboard
   - Navigate to: **Settings → Environment Variables**
   - Add new variable:
     - **Name**: `OCR_SPACE_API_KEY`
     - **Value**: Your API key from OCR.space
   - Select environments: **Production, Preview, Development**
   - Click **Save**

4. **Redeploy**
   - After adding the environment variable, redeploy your app
   - The system will automatically use the API key

## Troubleshooting

### Still Getting "Could not extract content" Error?

1. **Check Vercel Logs**
   - Go to Vercel Dashboard → Your Project → **Deployments**
   - Click on the latest deployment → **Functions** tab
   - Look for logs containing:
     - `Processing PDF with cloud OCR`
     - `OCR.space API response status`
     - `Cloud OCR extracted`
     - Any error messages

2. **Common Issues:**

   **Issue: Rate Limit Exceeded**
   - **Solution**: Get an OCR.space API key (see above)
   - Free tier has limits that may be reached

   **Issue: PDF Too Large**
   - **Limit**: 10MB per request (free tier)
   - **Solution**: Split large PDFs or get API key for higher limits

   **Issue: Network Timeout**
   - **Solution**: Large PDFs may timeout
   - Try smaller PDFs or get API key for faster processing

   **Issue: No Text Found**
   - **Solution**: The PDF might be:
     - Too low quality
     - Handwritten (OCR may struggle)
     - Blank or corrupted
   - Try entering topic manually

3. **Test with a Simple PDF**
   - Try uploading a simple text-based PDF first
   - Then try a scanned PDF
   - Check logs to see what's happening

## How to Check Logs

1. **Vercel Dashboard Method:**
   - Go to: https://vercel.com/dashboard
   - Select your project
   - Click **Deployments** → Latest deployment
   - Click **Functions** tab
   - Look for function logs

2. **Vercel CLI Method:**
   ```bash
   vercel logs [deployment-url]
   ```

3. **What to Look For:**
   - `Processing PDF with cloud OCR` - OCR started
   - `OCR.space API response status: 200` - Success
   - `OCR.space API response status: 429` - Rate limit
   - `Cloud OCR extracted X characters` - Success
   - `All cloud OCR methods failed` - Failure

## Environment Variables Summary

### Required (Already Set):
- `DATABASE_URL` - Your Neon DB connection
- `GOOGLE_AI_API_KEY` - For question generation
- `SECRET_KEY` - Flask secret key

### Optional (Recommended):
- `OCR_SPACE_API_KEY` - For better OCR reliability

## Testing

After adding the API key:

1. **Redeploy** your Vercel app
2. **Test with a scanned PDF**
3. **Check logs** to verify OCR is working
4. **Look for**: `Using OCR.space API key for better rate limits`

## Support

If issues persist:
1. Check Vercel logs for detailed error messages
2. Verify API key is set correctly in environment variables
3. Test with a simple PDF first
4. Check OCR.space API status: https://status.ocr.space/

## Alternative Solutions

If OCR.space doesn't work:
- The system will show a helpful error message
- You can always enter a topic manually
- Questions will still be generated from the topic

