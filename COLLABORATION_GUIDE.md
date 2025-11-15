# 👥 Collaboration Guide - Working Together on UniTest

This guide explains how multiple developers can work on the same project simultaneously.

## 🚀 Quick Setup for Team Members

### Step 1: Clone the Repository

Each team member should clone the repository:

```bash
git clone https://github.com/theakshatkhandelwal/UNITEST-EXAM.git
cd UNITEST-EXAM
```

### Step 2: Set Up Local Environment

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `env_example.txt` to `.env`
   - Add your own API keys and database URLs
   - **Important:** Each developer should use their own local database or a shared test database

### Step 3: Create Your Own Branch

**Never work directly on `main` branch!** Create your own feature branch:

```bash
# Create and switch to a new branch
git checkout -b your-name-feature-name

# Example:
git checkout -b akshat-add-feature
git checkout -b friend1-fix-bug
git checkout -b friend2-update-ui
```

## 🔄 Daily Workflow

### 1. Before Starting Work (Every Day)

```bash
# Switch to main branch
git checkout main

# Pull latest changes from GitHub
git pull origin main

# Switch back to your feature branch
git checkout your-branch-name

# Merge latest changes into your branch
git merge main
```

### 2. While Working

```bash
# Check what files you've changed
git status

# See what you've modified
git diff

# Stage your changes
git add .

# Commit with a clear message
git commit -m "Add: Description of what you did"

# Push to GitHub
git push origin your-branch-name
```

### 3. When Your Feature is Complete

**Option A: Create a Pull Request (Recommended)**

1. Push your branch to GitHub:
   ```bash
   git push origin your-branch-name
   ```

2. Go to GitHub: https://github.com/theakshatkhandelwal/UNITEST-EXAM
3. Click "Pull Requests" → "New Pull Request"
4. Select your branch and create PR
5. Add description of changes
6. Request review from team members
7. After approval, merge to `main`

**Option B: Merge Directly (For Small Changes)**

```bash
# Switch to main
git checkout main

# Pull latest
git pull origin main

# Merge your branch
git merge your-branch-name

# Push to GitHub
git push origin main
```

## 🛡️ Best Practices

### 1. Communication
- **Before starting work:** Tell your team what you're working on
- **If you're modifying shared files:** Coordinate with others
- **When stuck:** Ask for help early

### 2. Branch Naming
Use clear, descriptive names:
- ✅ `akshat-forgot-password`
- ✅ `friend1-fix-login-bug`
- ✅ `friend2-update-dashboard`
- ❌ `test`
- ❌ `changes`
- ❌ `fix`

### 3. Commit Messages
Write clear commit messages:
- ✅ `Add: Forgot password feature`
- ✅ `Fix: Login error handling`
- ✅ `Update: Dashboard UI styling`
- ❌ `fix`
- ❌ `changes`
- ❌ `update`

### 4. Pull Before Push
Always pull latest changes before pushing:
```bash
git pull origin main
# Resolve any conflicts
git push origin your-branch-name
```

### 5. Don't Commit Sensitive Data
Never commit:
- `.env` files
- API keys
- Passwords
- Personal database URLs

## 🔧 Handling Conflicts

If you get merge conflicts:

1. **Open the conflicted file** - You'll see markers like:
   ```
   <<<<<<< HEAD
   Your changes
   =======
   Their changes
   >>>>>>> branch-name
   ```

2. **Resolve the conflict:**
   - Keep your changes
   - Keep their changes
   - Combine both
   - Delete the conflict markers

3. **Stage and commit:**
   ```bash
   git add .
   git commit -m "Resolve merge conflicts"
   ```

## 📋 Recommended Workflow for 3 People

### Day 1: Setup
- All 3 people clone the repo
- Each creates their own branch
- Set up local environments

### Daily Workflow:
1. **Person 1:** Works on Feature A (e.g., user authentication)
2. **Person 2:** Works on Feature B (e.g., quiz creation)
3. **Person 3:** Works on Feature C (e.g., UI improvements)

### Coordination:
- **Morning:** Quick sync on what each person is working on
- **During day:** Work on separate features/files
- **End of day:** Push changes, create PRs
- **Review:** Review each other's PRs before merging

## 🎯 Dividing Work

### By Feature:
- **Person 1:** Backend/API routes
- **Person 2:** Frontend/Templates
- **Person 3:** Database/Testing

### By Page:
- **Person 1:** Login/Signup pages
- **Person 2:** Dashboard/Quiz pages
- **Person 3:** Admin/Results pages

### By Task:
- **Person 1:** New features
- **Person 2:** Bug fixes
- **Person 3:** UI/UX improvements

## 🚨 Common Issues & Solutions

### Issue: "Your branch is behind"
```bash
git checkout main
git pull origin main
git checkout your-branch
git merge main
```

### Issue: "Permission denied"
- Make sure you're added as a collaborator on GitHub
- Check you have push access

### Issue: "Can't push, remote has changes"
```bash
git pull origin main
# Resolve conflicts if any
git push origin your-branch
```

## 📚 Useful Git Commands

```bash
# See all branches
git branch -a

# See commit history
git log --oneline

# See what changed
git diff

# Undo local changes (careful!)
git checkout -- filename

# Create a new branch from main
git checkout main
git pull
git checkout -b new-feature
```

## 🔐 GitHub Access

To add collaborators:
1. Go to: https://github.com/theakshatkhandelwal/UNITEST-EXAM/settings/access
2. Click "Collaborators" → "Add people"
3. Enter their GitHub username/email
4. They'll receive an invitation

## ✅ Checklist for New Team Members

- [ ] Cloned the repository
- [ ] Set up virtual environment
- [ ] Installed dependencies
- [ ] Created `.env` file with API keys
- [ ] Created their own branch
- [ ] Tested the app locally
- [ ] Understood the workflow

## 💡 Tips

1. **Work on different files** when possible to avoid conflicts
2. **Commit often** with small, logical changes
3. **Pull before push** to stay updated
4. **Communicate** about what you're working on
5. **Test locally** before pushing
6. **Review PRs** before merging to main

---

**Need help?** Ask your team or check Git documentation: https://git-scm.com/doc

