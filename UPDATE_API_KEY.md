# 🔑 How to Update Gemini API Key in Vercel

## Quick Steps

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Sign in to your account

2. **Select Your Project**
   - Click on `unitest-ai-exam-platform` (or your project name)

3. **Go to Settings**
   - Click on **"Settings"** tab in the top navigation

4. **Environment Variables**
   - Click on **"Environment Variables"** in the left sidebar

5. **Update the Key**
   - Find `GOOGLE_AI_API_KEY` in the list
   - Click the **pencil/edit icon** next to it
   - **OR** if it doesn't exist, click **"Add New"**
   - **Name**: `GOOGLE_AI_API_KEY`
   - **Value**: `AIzaSyBCHB_9ahb5nfttLH9S5XFsUVzy3JEZGRw`
   - **Environment**: Select all (Production, Preview, Development)
   - Click **"Save"**

6. **Redeploy**
   - Go to **"Deployments"** tab
   - Click the **three dots** (⋯) on the latest deployment
   - Click **"Redeploy"**
   - **OR** just wait - Vercel will auto-redeploy on next push

## ✅ New API Key

```
AIzaSyBCHB_9ahb5nfttLH9S5XFsUVzy3JEZGRw
```

## 🔒 Security Note

- **Never commit API keys to GitHub**
- API keys are stored securely in Vercel environment variables
- The code reads from `GOOGLE_AI_API_KEY` environment variable
- No hardcoded keys in the codebase

## 🧪 Test After Update

1. Wait 1-2 minutes for redeploy
2. Visit: `https://www.unitest.in/quiz`
3. Try generating a quiz
4. Should work with the new API key!


