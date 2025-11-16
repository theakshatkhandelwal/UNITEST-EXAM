# 🛠️ Local Development Guide - Test Before Deploying

This guide helps you test changes locally **before** they go live on your website.

## 🎯 Why Test Locally?

- ✅ Test new features safely
- ✅ Fix bugs before users see them
- ✅ Verify everything works before deploying
- ✅ No risk of breaking your live website

---

## 🚀 Quick Start

### Step 1: Set Up Local Environment

1. **Create a `.env` file** (if you don't have one):
   ```bash
   # Windows PowerShell
   Copy-Item env_example.txt .env
   
   # Or manually copy and rename the file
   ```

2. **Edit `.env` file** with your local settings:
   ```env
   SECRET_KEY=your-local-secret-key-here
   FLASK_ENV=development
   DATABASE_URL=sqlite:///unittest_local.db
   GOOGLE_AI_API_KEY=your-google-ai-api-key-here
   OCR_SPACE_API_KEY=your-ocr-api-key-here  # Optional
   ```

   **Important**: Use a **different database** for local testing:
   - Production: `DATABASE_URL=postgresql://...` (from NeonDB)
   - Local: `DATABASE_URL=sqlite:///unittest_local.db` (SQLite file)

3. **Install dependencies** (if not already done):
   ```bash
   # Windows
   py -m pip install -r requirements.txt
   
   # Mac/Linux
   pip install -r requirements.txt
   ```

---

## 🧪 Testing Your Changes Locally

### Step 0: Initialize Database (First Time Only)

**Important**: Before running the app for the first time, you need to initialize the database:

```bash
# Windows
py init_local_db.py

# Mac/Linux
python init_local_db.py
```

This creates all the necessary database tables. You only need to do this once (or if you delete the database file).

### Method 1: Run Locally (Recommended)

1. **Start local server**:
   ```bash
   # Windows
   py run_local.py
   
   # Or standard way
   py app.py
   
   # Mac/Linux
   python run_local.py
   python app.py
   ```

2. **Open browser**: `http://localhost:5000`

3. **Test your changes**:
   - Create accounts
   - Test features
   - Check for errors
   - Verify everything works

4. **Stop server**: Press `Ctrl+C` in terminal

### Method 2: Use Development Branch (Advanced)

This keeps your `main` branch safe for production:

1. **Create a development branch**:
   ```bash
   git checkout -b development
   ```

2. **Make your changes** on the `development` branch

3. **Test locally**:
   ```bash
   # Windows
   py run_local.py
   
   # Mac/Linux
   python run_local.py
   ```

4. **If everything works**, merge to main:
   ```bash
   git checkout main
   git merge development
   git push
   ```

5. **If something breaks**, fix it on `development` branch first

---

## ✅ Pre-Deployment Checklist

Before pushing to production, test these:

- [ ] **Homepage loads** without errors
- [ ] **Login/Signup** works correctly
- [ ] **Dashboard** displays properly
- [ ] **Quiz creation** works (if you changed it)
- [ ] **Quiz taking** works (if you changed it)
- [ ] **Database operations** work (create, read, update)
- [ ] **No console errors** in browser (F12 → Console)
- [ ] **No Python errors** in terminal
- [ ] **All pages** load correctly
- [ ] **Mobile responsive** (test on phone or resize browser)

---

## 🔄 Workflow: Making Changes Safely

### Recommended Workflow:

```
1. Make changes locally
   ↓
2. Test locally (python app.py)
   ↓
3. Fix any bugs
   ↓
4. Test again
   ↓
5. Commit changes
   ↓
6. Push to GitHub
   ↓
7. Vercel auto-deploys (only if main branch)
```

### Safe Development Workflow (Using Branches):

```
1. Create development branch
   git checkout -b development
   ↓
2. Make changes
   ↓
3. Test locally
   python app.py
   ↓
4. Fix bugs, test again
   ↓
5. Commit to development branch
   git add .
   git commit -m "Add new feature"
   git push origin development
   ↓
6. Test on development branch
   ↓
7. If everything works:
   git checkout main
   git merge development
   git push origin main
   ↓
8. Production auto-deploys
```

---

## 🐛 Common Issues & Solutions

### Issue: "Database locked" error
**Solution**: Make sure you're using a different database file for local testing:
```env
DATABASE_URL=sqlite:///unittest_local.db
```

### Issue: "Module not found" error
**Solution**: Install dependencies:
```bash
# Windows
py -m pip install -r requirements.txt

# Mac/Linux
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution**: Use a different port:
```bash
# Windows PowerShell
$env:PORT=5001; python app.py

# Or edit app.py to use port 5001
```

### Issue: Changes not showing
**Solution**: 
- Clear browser cache (Ctrl+Shift+Delete)
- Restart the Flask server
- Check if you're editing the right file

---

## 📝 Testing Script

Create a simple test script to verify everything works:

```bash
# test_local.sh (for Mac/Linux)
#!/bin/bash
echo "🧪 Testing local setup..."
python app.py &
sleep 5
curl http://localhost:5000
echo "✅ Server is running!"
```

Or use Python:
```python
# test_local.py
import requests
import time
import subprocess
import sys

print("🧪 Starting local server test...")
# Start server in background, test, then stop
```

---

## 🎯 Best Practices

1. **Always test locally first**
   - Never push untested code
   - Test all affected features

2. **Use separate database for local**
   - Don't use production database locally
   - Use SQLite for local testing

3. **Check browser console**
   - Open DevTools (F12)
   - Check for JavaScript errors
   - Check Network tab for failed requests

4. **Test on different browsers**
   - Chrome, Firefox, Edge
   - Mobile view (responsive design)

5. **Keep production safe**
   - Use branches for risky changes
   - Test thoroughly before merging to main

---

## 🚨 Emergency: If You Break Production

If something goes wrong after deploying:

1. **Revert the last commit**:
   ```bash
   git revert HEAD
   git push
   ```

2. **Or rollback to previous version**:
   ```bash
   git log  # Find the last working commit
   git reset --hard <commit-hash>
   git push --force
   ```

3. **Check Vercel logs**:
   - Go to Vercel dashboard
   - Check deployment logs
   - Look for error messages

---

## 📚 Additional Resources

- **Flask Debug Mode**: Add to `app.py` for better error messages:
  ```python
  if __name__ == '__main__':
      app.run(debug=True)  # Only for local development!
  ```

- **Local Database Reset**: If you need to start fresh:
  ```bash
  rm unittest_local.db
  python app.py  # Will recreate database
  ```

---

## ✅ Quick Reference

| Task | Command |
|------|---------|
| Start local server | `python app.py` |
| Create dev branch | `git checkout -b development` |
| Test locally | Open `http://localhost:5000` |
| Check for errors | Browser F12 → Console |
| Stop server | `Ctrl+C` in terminal |
| Deploy to production | `git push origin main` |

---

**Remember**: Test locally, deploy confidently! 🚀

