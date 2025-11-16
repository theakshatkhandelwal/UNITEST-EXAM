# 🔄 Development Workflow - Test Before Deploy

## 🎯 Your Goal
Test changes locally **before** they affect your live website.

---

## 📋 Step-by-Step Workflow

### **Option 1: Simple Workflow (Recommended for Beginners)**

```
1. Make changes to your code
   ↓
2. Test locally:
   python run_local.py
   ↓
3. Open browser: http://localhost:5000
   ↓
4. Test everything works
   ↓
5. If OK → Commit and push
   If NOT OK → Fix and test again
```

### **Option 2: Branch Workflow (Safer for Production)**

```
1. Create development branch:
   git checkout -b development
   ↓
2. Make your changes
   ↓
3. Test locally:
   python run_local.py
   ↓
4. Test everything
   ↓
5. Commit to development branch:
   git add .
   git commit -m "Description of changes"
   git push origin development
   ↓
6. If everything works, merge to main:
   git checkout main
   git merge development
   git push origin main
   ↓
7. Production auto-deploys (Vercel)
```

---

## 🚀 Quick Start Commands

### First Time Setup:
```bash
# Windows PowerShell:
# 1. Create .env file (if not exists)
Copy-Item env_example.txt .env

# 2. Edit .env file - add your API keys
# Use a LOCAL database for testing:
DATABASE_URL=sqlite:///unittest_local.db

# 3. Install dependencies
py -m pip install -r requirements.txt

# 4. Run local test script
py test_local.py

# Mac/Linux:
# 1. Create .env file
cp env_example.txt .env

# 2-4. Same as above, but use 'python' instead of 'py'
```

### Daily Development:
```bash
# Windows:
py run_local.py
# Or: py app.py

# Mac/Linux:
python run_local.py
# Or: python app.py
```

---

## ✅ Testing Checklist

Before pushing to production, test:

- [ ] **Homepage** loads correctly
- [ ] **Login/Signup** works
- [ ] **Dashboard** displays
- [ ] **New features** work as expected
- [ ] **No errors** in browser console (F12)
- [ ] **No errors** in terminal
- [ ] **Database operations** work
- [ ] **Mobile view** looks good (resize browser)

---

## 🛡️ Safety Tips

### ✅ DO:
- ✅ Test locally first
- ✅ Use separate database for local testing
- ✅ Use development branch for risky changes
- ✅ Check browser console for errors
- ✅ Test all affected features

### ❌ DON'T:
- ❌ Push untested code
- ❌ Use production database locally
- ❌ Skip testing
- ❌ Deploy on Friday (hard to fix on weekend)

---

## 🐛 If Something Breaks

### Local Testing:
1. Check terminal for error messages
2. Check browser console (F12)
3. Fix the issue
4. Test again

### After Deploying:
1. Check Vercel deployment logs
2. If broken, revert:
   ```bash
   git revert HEAD
   git push
   ```

---

## 📝 Example: Adding a New Feature

```bash
# 1. Create development branch
git checkout -b feature/new-button

# 2. Make your changes
# Edit templates/home.html, app.py, etc.

# 3. Test locally
# Windows: py run_local.py
# Mac/Linux: python run_local.py

# 4. Open http://localhost:5000
# Test the new button works

# 5. If it works, commit
git add .
git commit -m "Add new button feature"
git push origin feature/new-button

# 6. Merge to main (if everything works)
git checkout main
git merge feature/new-button
git push origin main
```

---

## 🎯 Quick Reference

| Task | Windows Command | Mac/Linux Command |
|------|----------------|-------------------|
| Test setup | `py test_local.py` | `python test_local.py` |
| Run locally | `py run_local.py` | `python run_local.py` |
| Create branch | `git checkout -b development` | `git checkout -b development` |
| Test changes | Open `http://localhost:5000` | Open `http://localhost:5000` |
| Commit changes | `git add . && git commit -m "message"` | `git add . && git commit -m "message"` |
| Push to GitHub | `git push` | `git push` |
| Deploy to production | Push to `main` branch | Push to `main` branch |

---

## 💡 Pro Tips

1. **Always test locally first** - It's faster and safer
2. **Use development branch** - Keeps main branch stable
3. **Test on mobile** - Resize browser or use phone
4. **Check console** - Browser DevTools (F12) shows errors
5. **Small commits** - Easier to find and fix issues

---

**Remember**: Test locally → Deploy confidently! 🚀

