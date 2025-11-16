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
# 1. Create .env file (if not exists)
cp env_example.txt .env

# 2. Edit .env file - add your API keys
# Use a LOCAL database for testing:
DATABASE_URL=sqlite:///unittest_local.db

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run local test script
python test_local.py
```

### Daily Development:
```bash
# Start local server
python run_local.py

# Or use the standard way
python app.py
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
python run_local.py

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

| Task | Command |
|------|---------|
| Test setup | `python test_local.py` |
| Run locally | `python run_local.py` |
| Create branch | `git checkout -b development` |
| Test changes | Open `http://localhost:5000` |
| Commit changes | `git add . && git commit -m "message"` |
| Push to GitHub | `git push` |
| Deploy to production | Push to `main` branch (auto-deploys) |

---

## 💡 Pro Tips

1. **Always test locally first** - It's faster and safer
2. **Use development branch** - Keeps main branch stable
3. **Test on mobile** - Resize browser or use phone
4. **Check console** - Browser DevTools (F12) shows errors
5. **Small commits** - Easier to find and fix issues

---

**Remember**: Test locally → Deploy confidently! 🚀

