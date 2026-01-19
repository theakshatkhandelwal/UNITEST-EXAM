# 🔑 Recommended API Key Setup for Gemini

## ✅ **Recommended Model: `gemini-pro`**

**Why `gemini-pro`?**
- ✅ Most stable and widely available
- ✅ Works on free tier (1,500 requests/day)
- ✅ No "404 model not found" errors
- ✅ Reliable for production use

## 📋 **Current Setup**

Your code now uses:
1. **Primary**: `gemini-pro` (most stable)
2. **Fallback**: `gemini-1.5-pro` (if gemini-pro fails)

## 🔧 **API Key Configuration**

### **Your Current API Key:**
```
AIzaSyBCHB_9ahb5nfttLH9S5XFsUVzy3JEZGRw
```

### **How to Verify It Works:**

1. **Check API Key Status:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account
   - Verify the key is active

2. **Check Quota:**
   - Go to: https://console.cloud.google.com/
   - Navigate to: APIs & Services → Dashboard
   - Search: "Generative Language API"
   - Check "Quotas" tab

3. **Test the Model:**
   - The code automatically uses `gemini-pro`
   - If it fails, it tries `gemini-1.5-pro`
   - Both are free tier models

## ⚠️ **Models to Avoid**

- ❌ `gemini-2.0-flash` - **0 free tier quota** (will always fail)
- ❌ `gemini-1.5-flash` - **May not be available** (404 errors)

## 🚀 **After Deployment**

Once Vercel redeploys:
- ✅ Uses `gemini-pro` automatically
- ✅ Falls back to `gemini-1.5-pro` if needed
- ✅ No more "404 model not found" errors
- ✅ Quiz generation should work

## 💡 **If Still Not Working**

1. **Check Vercel Environment Variable:**
   - Vercel Dashboard → Settings → Environment Variables
   - Verify `GOOGLE_AI_API_KEY` is set correctly
   - Value: `AIzaSyBCHB_9ahb5nfttLH9S5XFsUVzy3JEZGRw`

2. **Check API Key Quota:**
   - Visit: https://aistudio.google.com/app/apikey
   - Check if quota is exceeded
   - Free tier: 1,500 requests/day

3. **Wait for Quota Reset:**
   - Quota resets at midnight UTC
   - Check current UTC time: https://time.is/UTC

4. **Upgrade to Paid Tier (Optional):**
   - If you need more quota
   - Enable billing in Google Cloud Console
   - Automatically upgrades to Tier 1

## 📊 **Free Tier Limits**

| Model | Requests/Day | Requests/Minute |
|-------|--------------|-----------------|
| `gemini-pro` | 1,500 | 60 |
| `gemini-1.5-pro` | 1,500 | 60 |

Both models have the same free tier limits, so `gemini-pro` is recommended for stability.


