# 🆓 Gemini Free Tier Models - Quick Guide

## ✅ **FREE Models (Use These)**

### **1. gemini-1.5-flash** ⭐ **BEST CHOICE**
- **Status**: ✅ **Best free tier option**
- **Quota**: 15 requests per minute, 1,500 per day
- **Speed**: Fastest response time
- **Use**: Primary model for quiz generation

### **2. gemini-pro**
- **Status**: ✅ **Most stable, widely available**
- **Quota**: 60 requests per minute, 1,500 per day
- **Speed**: Moderate
- **Use**: Fallback if gemini-1.5-flash fails

### **3. gemini-1.5-pro**
- **Status**: ✅ Available but slower
- **Quota**: Lower than flash version
- **Speed**: Slower than flash
- **Use**: Alternative fallback

---

## ❌ **NOT Free (Avoid These)**

### **gemini-2.0-flash**
- **Status**: ❌ **0 free tier quota**
- **Issue**: Will always show "Quota exceeded" or "API configuration error"
- **Solution**: Don't use this model - it requires paid tier

---

## 🔧 **How to Use**

The code will automatically:
1. **Try `gemini-1.5-flash` first** (best free option)
2. **Fall back to `gemini-pro`** if flash fails
3. **Fall back to `gemini-1.5-pro`** as last resort

---

## 📊 **Check Your Quota**

1. **Google AI Studio**: https://aistudio.google.com/app/apikey
   - Sign in → Check "Usage" tab
   - See daily requests used vs limit

2. **Google Cloud Console**: https://console.cloud.google.com/
   - APIs & Services → Dashboard
   - Search "Generative Language API"
   - Check "Quotas" tab

---

## 🚀 **Quick Fix**

If you see "API configuration error" or "Quota exceeded":
1. **Wait 1-2 minutes** (rate limit resets)
2. **Check quota**: https://aistudio.google.com/app/apikey
3. **Verify API key** is set in Vercel environment variables
4. **The code will auto-select** the best working free model

---

## 💡 **Summary**

- ✅ **Use**: `gemini-1.5-flash` (primary) or `gemini-pro` (fallback)
- ❌ **Avoid**: `gemini-2.0-flash` (no free quota)
- 🔄 **Auto-selection**: Code picks the best available model automatically

