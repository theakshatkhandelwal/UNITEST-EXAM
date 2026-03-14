# 🔍 Google Gemini API Usage Monitoring Guide

This guide explains how to monitor your Google Gemini API usage and check when you're approaching your limits.

## 📊 Google Gemini API Free Tier Limits

### Current Free Tier Limits (as of 2024):
- **Requests per minute (RPM)**: 60 requests/minute
- **Requests per day (RPD)**: 1,500 requests/day
- **Tokens per minute (TPM)**: 32,000 tokens/minute
- **Tokens per day (TPD)**: 1,500,000 tokens/day

### Paid Tier Limits:
- Higher limits available based on your billing plan
- Check your specific limits in Google Cloud Console

## 🔐 How to Check Your API Usage

### Method 1: Google Cloud Console (Recommended)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Navigate to APIs & Services**
   - Click on "APIs & Services" in the left sidebar
   - Select "Dashboard" or "Quotas"

3. **Find Gemini API**
   - Search for "Generative Language API" or "Gemini API"
   - Click on it to view details

4. **Check Usage Metrics**
   - View "Quotas" tab to see your limits
   - Check "Metrics" tab to see current usage
   - Look for:
     - Requests per minute/day
     - Tokens per minute/day
     - Error rates

5. **Set Up Alerts** (Recommended)
   - Go to "Quotas" → Select a quota → Click "Edit Quotas"
   - Set up email alerts when you reach 50%, 75%, 90% of your limit

### Method 2: Google AI Studio

1. **Visit Google AI Studio**
   - Go to: https://aistudio.google.com/
   - Sign in with your Google account

2. **Check API Usage**
   - Click on your profile/account icon
   - Navigate to "API Usage" or "Billing"
   - View your current usage and limits

### Method 3: Using the Monitoring Script

We've created a Python script (`check_gemini_usage.py`) that you can run to check your API usage programmatically.

## ⚠️ What Happens When You Reach Limits?

### Rate Limit Exceeded (429 Error)
- **Symptom**: API calls start failing with HTTP 429 status
- **Message**: "Resource has been exhausted (e.g. check quota)"
- **Solution**: Wait for the rate limit window to reset (usually 1 minute)

### Daily Quota Exceeded
- **Symptom**: All API calls fail until the next day
- **Message**: "Quota exceeded"
- **Solution**: 
  - Wait until quota resets (usually at midnight UTC)
  - Upgrade to paid tier for higher limits

## 🛠️ Monitoring in Your Application

### Error Handling
The application should handle quota errors gracefully. Check for these error types:

```python
try:
    response = model.generate_content(prompt)
except Exception as e:
    if 'quota' in str(e).lower() or '429' in str(e):
        # Handle quota exceeded
        print("API quota exceeded. Please try again later.")
    elif 'rate limit' in str(e).lower():
        # Handle rate limit
        print("Rate limit reached. Please wait a moment.")
```

### Usage Tracking
Consider implementing usage tracking in your database to monitor:
- Number of API calls per day
- Tokens used per request
- Error rates
- Cost estimation

## 📈 Best Practices

1. **Monitor Regularly**
   - Check your usage daily during peak usage periods
   - Set up alerts at 50%, 75%, and 90% of limits

2. **Optimize API Calls**
   - Cache responses when possible
   - Batch requests when appropriate
   - Use shorter prompts to reduce token usage

3. **Handle Errors Gracefully**
   - Implement retry logic with exponential backoff
   - Show user-friendly error messages
   - Log errors for debugging

4. **Plan for Growth**
   - Monitor usage trends
   - Upgrade to paid tier before hitting limits
   - Consider multiple API keys for load balancing

## 🔔 Setting Up Alerts

### In Google Cloud Console:
1. Go to "APIs & Services" → "Quotas"
2. Select "Generative Language API"
3. Click on a quota (e.g., "Requests per day")
4. Click "Edit Quotas"
5. Set alert thresholds:
   - 50% of quota
   - 75% of quota
   - 90% of quota
6. Add email addresses to receive alerts

## 📝 Example: Checking Usage Programmatically

See `check_gemini_usage.py` for a complete example of how to programmatically check your API usage and limits.

## 🆘 Troubleshooting

### "Quota Exceeded" Error
- **Check**: Google Cloud Console → Quotas
- **Solution**: Wait for reset or upgrade plan

### "Rate Limit" Error
- **Check**: Requests per minute usage
- **Solution**: Implement request throttling or wait

### API Key Not Working
- **Check**: API key is valid and enabled
- **Check**: Generative Language API is enabled in your project
- **Solution**: Regenerate API key if needed

## 📚 Additional Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Pricing Information](https://ai.google.dev/pricing)




