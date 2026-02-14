# 🔐 Fix: "Permission denied" - GitHub Authentication

## ❌ The Problem

**Error:**
```
remote: Permission to flourencenadarphd-a11y/guis.git denied to FlourenceNadar.
fatal: unable to access 'https://github.com/...': The requested URL returned error: 403
```

**What this means:**
- Git is trying to use username "FlourenceNadar"
- But the repository is under "flourencenadarphd-a11y"
- Authentication is failing (403 = Forbidden)

---

## ✅ Solutions (Try in Order)

### Solution 1: Use Personal Access Token (Recommended)

GitHub no longer accepts passwords. You need a Personal Access Token.

#### Step 1: Create Personal Access Token

1. **Go to**: https://github.com/settings/tokens
2. **Click**: "Generate new token" → "Generate new token (classic)"
3. **Fill in:**
   - **Note**: "GUIS Deployment"
   - **Expiration**: 90 days (or your choice)
   - **Select scopes**: Check `repo` (this gives full repository access)
4. **Click**: "Generate token"
5. **IMPORTANT**: Copy the token immediately! (You won't see it again)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### Step 2: Use Token When Pushing

When Git asks for credentials:
- **Username**: `flourencenadarphd-a11y` (your GitHub username)
- **Password**: Paste your Personal Access Token (not your GitHub password!)

#### Step 3: Push Again

```bash
cd C:\guis
git push -u origin main
```

When prompted:
- Username: `flourencenadarphd-a11y`
- Password: [paste your token]

---

### Solution 2: Check Repository Access

**Verify the repository exists and you have access:**

1. **Go to**: https://github.com/flourencenadarphd-a11y/guis
2. **Check if you can see it:**
   - ✅ If you see the repository → You have access, use Solution 1
   - ❌ If you see "404 Not Found" → Repository doesn't exist, use Solution 3

---

### Solution 3: Create Repository First

**If repository doesn't exist:**

1. **Go to**: https://github.com/new
2. **Fill in:**
   - **Repository name**: `guis`
   - **Description**: "Global University Intelligence System"
   - **Visibility**: Public (recommended)
   - **DO NOT** initialize with README, .gitignore, or license
3. **Click**: "Create repository"
4. **Then push** (use Solution 1 for authentication)

---

### Solution 4: Update Git Credentials

**Clear old credentials and use new ones:**

```bash
# Clear cached credentials
git config --global --unset credential.helper
git config --global credential.helper store

# Try pushing again (will prompt for new credentials)
git push -u origin main
```

**When prompted:**
- Username: `flourencenadarphd-a11y`
- Password: [Your Personal Access Token]

---

### Solution 5: Use SSH Instead of HTTPS

**If HTTPS keeps failing, use SSH:**

#### Step 1: Generate SSH Key (if you don't have one)

```bash
# Check if you have SSH key
ls ~/.ssh/id_rsa.pub

# If not, generate one
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for all prompts (use default location, no passphrase)
```

#### Step 2: Add SSH Key to GitHub

1. **Copy your SSH key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Copy the output
   ```

2. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Title: "GUIS Deployment"
   - Key: Paste your SSH key
   - Click "Add SSH key"

#### Step 3: Change Remote to SSH

```bash
cd C:\guis
git remote set-url origin git@github.com:flourencenadarphd-a11y/guis.git
git push -u origin main
```

---

## 🎯 Quick Fix (Recommended)

**Easiest solution - Use Personal Access Token:**

1. **Create token**: https://github.com/settings/tokens
   - Generate new token (classic)
   - Select `repo` scope
   - Copy the token

2. **Push with token:**
   ```bash
   cd C:\guis
   git push -u origin main
   ```
   - Username: `flourencenadarphd-a11y`
   - Password: [paste token]

3. **Done!** ✅

---

## 🔍 Verify It Worked

After pushing:

1. **Go to**: https://github.com/flourencenadarphd-a11y/guis
2. **Check that you see:**
   - ✅ `streamlit_app.py`
   - ✅ `backend/` folder
   - ✅ `data/` folder
   - ✅ `requirements.txt`
   - ✅ Other files

**If files are there**: ✅ Success! Now deploy to Streamlit Cloud.

---

## 📝 After Fixing Authentication

Once your code is pushed to GitHub:

1. **Go to Streamlit Cloud**: https://share.streamlit.io
2. **Click "New app"**
3. **Select**: `flourencenadarphd-a11y/guis`
4. **Main file**: `streamlit_app.py`
5. **Deploy!**

**Now it should work!** ✅

---

## 💡 Why This Happened

- GitHub stopped accepting passwords in 2021
- You need a Personal Access Token instead
- The token acts as your password
- It's more secure and can be revoked

---

**Fix the authentication, push your code, then deploy to Streamlit Cloud! 🚀**

