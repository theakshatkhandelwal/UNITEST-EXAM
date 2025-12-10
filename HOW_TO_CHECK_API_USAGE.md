# 🔍 How to Check Which API is Being Used

## 📊 **Method 1: Check Vercel Logs (Recommended)**

### Steps:
1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Sign in to your account

2. **Select Your Project**
   - Click on your project (unitest.in)

3. **Go to Logs**
   - Click **"Deployments"** tab
   - Click on the **latest deployment**
   - Click **"Logs"** tab (or **"Functions"** → **"View Logs"**)

4. **Generate a Quiz**
   - Visit: `https://www.unitest.in/quiz`
   - Try generating a quiz
   - Go back to Vercel logs

5. **Look for These Messages:**

### ✅ **If OpenRouter is Working (Primary):**
```
============================================================
📝 QUIZ GENERATION STARTED
   Topic: [your topic]
   Type: mcq, Difficulty: beginner, Count: 5
============================================================
✅ OpenRouter API key found
🚀 PRIMARY: Attempting OpenRouter API...
🔄 Trying OpenRouter model: meta-llama/llama-3.1-8b-instruct:free
✅ OpenRouter SUCCESS: Model 'meta-llama/llama-3.1-8b-instruct:free' generated 5 questions
✅ SUCCESS: Quiz generated using OpenRouter API (primary)
============================================================
```

### 🔄 **If Gemini is Used (Fallback):**
```
============================================================
📝 QUIZ GENERATION STARTED
   Topic: [your topic]
   Type: mcq, Difficulty: beginner, Count: 5
============================================================
✅ OpenRouter API key found
🚀 PRIMARY: Attempting OpenRouter API...
⚠️ OpenRouter failed: [error message]
🔄 FALLBACK: Switching to Gemini API...
🔄 FALLBACK: Attempting Gemini API...
✓ Gemini: Using available model: gemini-2.5-flash
✅ SUCCESS: Quiz generated using Gemini API (fallback)
============================================================
```

### ⚠️ **If OpenRouter Key Not Set:**
```
============================================================
📝 QUIZ GENERATION STARTED
   Topic: [your topic]
   Type: mcq, Difficulty: beginner, Count: 5
============================================================
⚠️ OpenRouter API key not found - using Gemini as primary
🔄 FALLBACK: Attempting Gemini API...
✓ Gemini: Using available model: gemini-2.5-flash
✅ SUCCESS: Quiz generated using Gemini API (fallback)
============================================================
```

---

## 📊 **Method 2: Check Browser Console (For Frontend)**

1. **Open Browser Developer Tools**
   - Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Go to **"Console"** tab

2. **Generate a Quiz**
   - The logs won't show API details here, but you can see if quiz generation succeeds

---

## 📊 **Method 3: Add a Test Endpoint (Optional)**

I can add a test endpoint that shows which API is configured. Would you like me to add this?

---

## 🔍 **What to Look For:**

### **OpenRouter Working:**
- ✅ `🚀 PRIMARY: Attempting OpenRouter API...`
- ✅ `✅ OpenRouter SUCCESS: Model '...' generated X questions`
- ✅ `✅ SUCCESS: Quiz generated using OpenRouter API (primary)`

### **Gemini Used as Fallback:**
- ⚠️ `⚠️ OpenRouter failed: ...`
- 🔄 `🔄 FALLBACK: Switching to Gemini API...`
- ✅ `✅ SUCCESS: Quiz generated using Gemini API (fallback)`

### **OpenRouter Key Not Set:**
- ⚠️ `⚠️ OpenRouter API key not found - using Gemini as primary`
- 🔄 `🔄 FALLBACK: Attempting Gemini API...`

---

## 🧪 **Quick Test:**

1. **Test with OpenRouter:**
   - Make sure `OPENROUTER_API_KEY` is set in Vercel
   - Generate a quiz
   - Check logs - should see `🚀 PRIMARY: Attempting OpenRouter API...`

2. **Test Fallback:**
   - Temporarily remove `OPENROUTER_API_KEY` from Vercel (or set wrong key)
   - Generate a quiz
   - Check logs - should see `🔄 FALLBACK: Attempting Gemini API...`

---

## 📝 **Summary:**

- **Primary API**: OpenRouter (if key is set)
- **Fallback API**: Gemini (if OpenRouter fails or not configured)
- **Logs show**: Clear indicators of which API is being used
- **Location**: Vercel Dashboard → Deployments → Latest → Logs

---

**The logs will clearly show which API is being used!** 🎯

