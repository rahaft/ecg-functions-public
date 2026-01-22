# Complete Deploy Script Guide

## 🚀 New Deploy Script: `deploy_complete.ps1`

A comprehensive script that:
- ✅ Updates version number (auto-increments)
- ✅ Updates build timestamp
- ✅ Commits to Git
- ✅ Pushes to GitHub
- ✅ Deploys to Firebase

---

## 📋 Usage

### Basic (Patch Version Bump):
```powershell
.\deploy_complete.ps1
```

This will:
- Increment patch version (e.g., 2.3.3 → 2.3.4)
- Update build timestamp
- Commit and push to GitHub
- Deploy to Firebase

### Minor Version Bump:
```powershell
.\deploy_complete.ps1 -VersionBump minor
```

### Major Version Bump:
```powershell
.\deploy_complete.ps1 -VersionBump major
```

### Custom Commit Message:
```powershell
.\deploy_complete.ps1 -CommitMessage "Added pagination and lazy loading"
```

### Skip Git (Only Deploy):
```powershell
.\deploy_complete.ps1 -SkipGit
```

### Skip Deploy (Only Git):
```powershell
.\deploy_complete.ps1 -SkipDeploy
```

### Both Options:
```powershell
.\deploy_complete.ps1 -SkipGit -SkipDeploy
```

---

## 🔄 What It Does

### Step 1: Update Version
- Reads current version from `gallery.html`
- Increments based on `VersionBump` parameter
- Updates version in all HTML files
- Generates new build timestamp

### Step 2: Git Operations
- Stages all changes
- Commits with message (auto-generated or custom)
- Pushes to GitHub

### Step 3: Deploy
- Deploys to Firebase Hosting
- Shows deployment URL

---

## 📝 Version Format

**Current:** `2.3.3`  
**After patch bump:** `2.3.4`  
**After minor bump:** `2.4.0`  
**After major bump:** `3.0.0`

**Build Timestamp:** `2026.01.21.1430` (YYYY.MM.DD.HHMM)  
**Build Date:** `1/21/2026, 2:30:00 PM`

---

## ⚙️ Files Updated

The script updates version in:
- `public/gallery.html` - Main version constant
- `public/index.html` - If version info exists
- `public/visualization.html` - If version info exists
- Other HTML files with version info

---

## 🔍 Prerequisites

1. **Git configured:**
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **GitHub remote set:**
   ```powershell
   git remote -v  # Should show origin
   ```

3. **Firebase CLI installed:**
   ```powershell
   npm install -g firebase-tools
   firebase login
   ```

4. **Firebase project initialized:**
   ```powershell
   firebase init
   ```

---

## 📋 Example Workflow

```powershell
# Make your changes to code...

# Deploy with auto version bump
.\deploy_complete.ps1

# Or with custom message
.\deploy_complete.ps1 -CommitMessage "Fixed gallery pagination"

# Or just update version without deploying
.\deploy_complete.ps1 -SkipDeploy
```

---

## ⚠️ Notes

- **Version is read from `gallery.html`** - Make sure it exists
- **Git operations are optional** - Use `-SkipGit` if needed
- **Deployment is optional** - Use `-SkipDeploy` if needed
- **Auto-commit message** - Generated if not provided

---

## 🎯 Quick Deploy

For fastest deployment:
```powershell
.\deploy_complete.ps1
```

That's it! One command does everything. 🚀
