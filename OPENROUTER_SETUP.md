# 🚀 OpenRouter Setup Guide (Fallback API)

## ✅ **What I Just Added**

Your code now **automatically uses OpenRouter** as a fallback when Gemini fails! This means:
- ✅ **No more failures** - If Gemini fails, OpenRouter takes over automatically
- ✅ **Free tier available** - 100K tokens/month free
- ✅ **Multiple models** - Tries free models first
- ✅ **Zero code changes needed** - Just add the API key!

---

## 🔑 **Quick Setup (2 minutes)**

### Step 1: Get OpenRouter API Key
1. Visit: **https://openrouter.ai/keys**
2. Sign up (free) or sign in
3. Click **"Create Key"**
4. Copy your API key

### Step 2: Add to Vercel
1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Click **"Add New"**
3. **Name**: `OPENROUTER_API_KEY`
4. **Value**: Paste your API key
5. Select **all environments** (Production, Preview, Development)
6. Click **"Save"**

### Step 3: Redeploy
- Vercel will auto-redeploy, or manually trigger a redeploy

---

## 🎯 **How It Works**

1. **First**: Tries Gemini API (your current setup)
2. **If Gemini fails**: Automatically switches to OpenRouter
3. **OpenRouter tries**:
   - `meta-llama/llama-3.1-8b-instruct:free` (completely free)
   - `mistralai/mistral-7b-instruct:free` (free)
   - `openai/gpt-3.5-turbo` (free tier available)

---

## 💰 **Cost**

- **Free tier**: 100,000 tokens/month
- **After free tier**: ~$0.0001 per 1K tokens (very cheap)
- **Example**: 100 quiz generations ≈ $0.01

---

## ✅ **Benefits**

1. ✅ **Automatic failover** - No code changes needed
2. ✅ **Free tier** - 100K tokens/month
3. ✅ **Reliable** - Multiple models to try
4. ✅ **Fast** - Quick response times
5. ✅ **No quota issues** - Unlike Gemini

---

## 🧪 **Test It**

1. **Without OpenRouter key**: Works with Gemini only (current behavior)
2. **With OpenRouter key**: Automatically uses OpenRouter if Gemini fails
3. **Check logs**: You'll see `🔄 Attempting fallback to OpenRouter API...` when it switches

---

## 📝 **Optional: Use OpenRouter as Primary**

If you want to use OpenRouter as the **primary** API instead of Gemini:

1. Set `OPENROUTER_API_KEY` in Vercel
2. Leave `GOOGLE_AI_API_KEY` empty (or remove it)
3. The code will automatically use OpenRouter

---

## 🆘 **Troubleshooting**

**Q: Do I need both API keys?**  
A: No! You can use just OpenRouter if you want. Gemini is optional now.

**Q: Will it cost money?**  
A: Only after you use 100K tokens/month (free tier). Very unlikely for quiz generation.

**Q: Which is better - Gemini or OpenRouter?**  
A: OpenRouter is more reliable (no quota issues), but Gemini is free if it works. Having both gives you the best of both worlds!

---

## 🎉 **You're All Set!**

Once you add the `OPENROUTER_API_KEY` to Vercel, your quiz generation will be **much more reliable**!


