# 👥 Adding Collaborators - Quick Guide

## Step-by-Step Instructions

### Step 1: Go to Repository Settings

1. Open your repository: https://github.com/theakshatkhandelwal/UNITEST-EXAM
2. Click on **"Settings"** tab (top right of the repository page)
3. In the left sidebar, click on **"Collaborators"** (under "Access" section)

### Step 2: Add Collaborators

1. Click the **"Add people"** button
2. In the search box, enter one of these usernames:
   - `Ajitesh-004` (for Ajitesh Kumara)
   - `abhishekamaresh` (for Abhishek A)
3. Select the user from the dropdown
4. Choose permission level: **"Write"** (allows them to push code)
5. Click **"Add [username] to this repository"**
6. Repeat for the second collaborator

### Step 3: Collaborators Accept Invitation

- Each collaborator will receive an email invitation
- They need to:
  1. Check their email
  2. Click the invitation link
  3. Accept the invitation
  4. They'll now have access to the repository

## Alternative: Direct Link

You can also use this direct link:
```
https://github.com/theakshatkhandelwal/UNITEST-EXAM/settings/access
```

## What Each Collaborator Can Do

With **"Write"** access, they can:
- ✅ Clone the repository
- ✅ Create branches
- ✅ Push code to their branches
- ✅ Create Pull Requests
- ✅ Review code
- ❌ Cannot delete the repository
- ❌ Cannot change repository settings

## Verification

After adding them, you should see:
- Their GitHub usernames listed under "Collaborators"
- Status: "Pending" (until they accept) or "Active" (after acceptance)

## Next Steps for Collaborators

Once they accept the invitation, they should:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theakshatkhandelwal/UNITEST-EXAM.git
   cd UNITEST-EXAM
   ```

2. **Create their own branch:**
   ```bash
   # Ajitesh
   git checkout -b ajitesh-feature-name
   
   # Abhishek
   git checkout -b abhishek-feature-name
   ```

3. **Set up their local environment:**
   - Create virtual environment
   - Install dependencies: `pip install -r requirements.txt`
   - Set up `.env` file with their own API keys

4. **Read the COLLABORATION_GUIDE.md** for detailed workflow

## Troubleshooting

**If you can't find "Collaborators" option:**
- Make sure you're the repository owner
- Check that the repository is not archived
- Verify you have admin access

**If collaborator can't accept invitation:**
- Check their email (including spam folder)
- They can also accept via GitHub notifications
- Or you can resend the invitation

**If collaborator can't push:**
- Make sure they accepted the invitation
- Verify they have "Write" access (not "Read")
- They should clone using HTTPS, not SSH (unless they've set up SSH keys)

## Quick Reference

- **Repository**: https://github.com/theakshatkhandelwal/UNITEST-EXAM
- **Settings**: https://github.com/theakshatkhandelwal/UNITEST-EXAM/settings
- **Collaborators**: https://github.com/theakshatkhandelwal/UNITEST-EXAM/settings/access
- **Ajitesh's GitHub**: https://github.com/Ajitesh-004
- **Abhishek's GitHub**: https://github.com/abhishekamaresh

