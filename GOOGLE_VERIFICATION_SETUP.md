# Google Search Console Verification Setup

## Step 1: Download the Verification File

1. In Google Search Console, click the **"Download"** button next to `google77cd707098d48f23.html`
2. Save the file to your computer

## Step 2: Add the File to Your Project

1. Place the downloaded `google77cd707098d48f23.html` file in the `static/` folder of your project
2. The route to serve this file has already been added to both `app.py` and `api/index.py`

## Step 3: Push to GitHub

```bash
git add static/google77cd707098d48f23.html
git commit -m "Add Google Search Console verification file"
git push
```

## Step 4: Verify in Google Search Console

1. Wait for Vercel to redeploy (1-2 minutes)
2. Test the file is accessible: Visit `https://unitest-ai-exam-platform.vercel.app/google77cd707098d48f23.html`
3. If the file loads correctly, go back to Google Search Console
4. Click the **"VERIFY"** button
5. You should see a success message!

## Step 5: Submit Your Sitemap

After verification:
1. Go to **"Sitemaps"** in Google Search Console
2. Enter: `https://unitest-ai-exam-platform.vercel.app/sitemap.xml`
3. Click **"Submit"**

## Important Notes

- **Don't delete the verification file** - Google needs it to stay verified
- The verification file route is already set up in the code
- Your sitemap and robots.txt have been updated with the correct URL

---

**Your Site URL:** `https://unitest-ai-exam-platform.vercel.app/`

