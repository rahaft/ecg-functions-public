# Quick Deploy - One Command

## 🚀 Deploy Everything

```powershell
.\deploy_complete.ps1
```

**That's it!** This single command:
- ✅ Updates version (auto-increments patch: 2.3.3 → 2.3.4)
- ✅ Updates build timestamp
- ✅ Commits to Git
- ✅ Pushes to GitHub
- ✅ Deploys to Firebase

---

## 📋 Options

### Version Bump Type:
```powershell
.\deploy_complete.ps1 -VersionBump patch   # 2.3.3 → 2.3.4 (default)
.\deploy_complete.ps1 -VersionBump minor   # 2.3.3 → 2.4.0
.\deploy_complete.ps1 -VersionBump major   # 2.3.3 → 3.0.0
```

### Custom Commit Message:
```powershell
.\deploy_complete.ps1 -CommitMessage "Added pagination feature"
```

### Skip Operations:
```powershell
.\deploy_complete.ps1 -SkipGit      # Skip Git commit/push
.\deploy_complete.ps1 -SkipDeploy   # Skip Firebase deployment
```

---

## 📝 What Gets Updated

- **Version:** `2.3.3` → `2.3.4` (in all HTML files)
- **Build Timestamp:** `2026.01.21.1430` (auto-generated)
- **Build Date:** `1/21/2026, 2:30:00 PM` (auto-generated)

---

## ✅ Prerequisites

1. **Git configured** (user.name, user.email)
2. **GitHub remote** set up
3. **Firebase CLI** installed and logged in

---

**One command to deploy it all!** 🚀
