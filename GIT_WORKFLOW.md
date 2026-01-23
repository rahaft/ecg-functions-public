# Git Workflow Sequence

## Standard Git Push Sequence

### 1. Check Status
```powershell
git status
```
See what files have been modified.

### 2. Stage Changes
```powershell
# Stage specific files
git add public/gallery.html
git add functions/index.js

# Or stage all changes
git add .
```

### 3. Commit Changes
```powershell
git commit -m "Your commit message here"
```

### 4. Push to Remote
```powershell
git push origin main
```

---

## Complete Sequence (Step by Step)

```powershell
# 1. Check what changed
git status

# 2. Review changes (optional)
git diff

# 3. Stage files
git add .

# 4. Commit
git commit -m "Description of changes"

# 5. Push
git push origin main
```

---

## Using the Automated Script

The `deploy_complete.ps1` script automates this:

```powershell
.\deploy_complete.ps1 -CommitMessage "Your message"
```

This script:
1. Updates version numbers
2. Stages all changes (`git add .`)
3. Commits with message (`git commit`)
4. Pushes to GitHub (`git push`)
5. Deploys to Firebase (`firebase deploy --only hosting`)

---

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| Check status | `git status` | See modified files |
| Stage files | `git add .` | Prepare files for commit |
| Commit | `git commit -m "message"` | Save changes locally |
| Push | `git push origin main` | Upload to GitHub |

---

## Common Workflows

### Just Push Changes (No Deployment)
```powershell
git add .
git commit -m "Updated gallery features"
git push origin main
```

### Push and Deploy
```powershell
git add .
git commit -m "Updated gallery features"
git push origin main
firebase deploy --only hosting
```

### Use Automated Script (Recommended)
```powershell
.\deploy_complete.ps1 -CommitMessage "Updated gallery features"
```
