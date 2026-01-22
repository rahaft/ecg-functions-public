# Complete Deployment Script
# Updates version, commits to Git, pushes to GitHub, and deploys

param(
    [string]$VersionBump = "patch",
    [string]$CommitMessage = "",
    [switch]$SkipGit = $false,
    [switch]$SkipDeploy = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current version from gallery.html
$galleryFile = "public\gallery.html"
if (-not (Test-Path $galleryFile)) {
    Write-Host "ERROR: gallery.html not found!" -ForegroundColor Red
    exit 1
}

$galleryContent = Get-Content $galleryFile -Raw
if ($galleryContent -match "const APP_VERSION = '(\d+)\.(\d+)\.(\d+)'") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    $patch = [int]$matches[3]
    $currentVersion = "$major.$minor.$patch"
} else {
    Write-Host "ERROR: Could not find version in gallery.html" -ForegroundColor Red
    exit 1
}

# Auto-increment patch version by default (unless specified)
if ($VersionBump -eq "patch" -and $PSBoundParameters.ContainsKey('VersionBump') -eq $false) {
    # Version will be incremented in the switch statement below
}

Write-Host "Current version: $currentVersion" -ForegroundColor Yellow

# Calculate new version
switch ($VersionBump.ToLower()) {
    "major" {
        $newMajor = $major + 1
        $newMinor = 0
        $newPatch = 0
    }
    "minor" {
        $newMajor = $major
        $newMinor = $minor + 1
        $newPatch = 0
    }
    "patch" {
        $newMajor = $major
        $newMinor = $minor
        $newPatch = $patch + 1
    }
    default {
        Write-Host "ERROR: Invalid version bump: $VersionBump (use: patch, minor, or major)" -ForegroundColor Red
        exit 1
    }
}

$newVersion = "$newMajor.$newMinor.$newPatch"
Write-Host "New version: $newVersion" -ForegroundColor Green
Write-Host ""

# Generate build timestamp
$buildTimestamp = Get-Date -Format "yyyy.MM.dd.HHmm"
$buildDate = Get-Date -Format "M/d/yyyy, h:mm:ss tt"

Write-Host "Build timestamp: $buildTimestamp" -ForegroundColor Cyan
Write-Host "Build date: $buildDate" -ForegroundColor Cyan
Write-Host ""

# Step 1: Update version in all files
Write-Host "Step 1: Updating version in files..." -ForegroundColor Yellow

# Update gallery.html
$galleryContent = $galleryContent -replace "const APP_VERSION = '\d+\.\d+\.\d+'", "const APP_VERSION = '$newVersion'"
$galleryContent = $galleryContent -replace "const BUILD_TIMESTAMP = [^;]+;", "const BUILD_TIMESTAMP = '$buildTimestamp';"
Set-Content -Path $galleryFile -Value $galleryContent -NoNewline
Write-Host "  Updated gallery.html (version: $newVersion, build: $buildTimestamp)" -ForegroundColor Green

# Update other HTML files if they have version info
$htmlFiles = @("public\index.html", "public\visualization.html", "public\training_viewer.html", "public\digitization_test.html")
foreach ($file in $htmlFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match "APP_VERSION|Version:") {
            $content = $content -replace "const APP_VERSION = '\d+\.\d+\.\d+'", "const APP_VERSION = '$newVersion'"
            $content = $content -replace "Version: \d+\.\d+\.\d+", "Version: $newVersion"
            Set-Content -Path $file -Value $content -NoNewline
            Write-Host "  Updated $file" -ForegroundColor Green
        }
    }
}

Write-Host ""

# Step 2: Git operations
if (-not $SkipGit) {
    Write-Host "Step 2: Git operations..." -ForegroundColor Yellow
    
    # Check if git repo
    if (-not (Test-Path ".git")) {
        Write-Host "  Not a git repository, skipping git operations" -ForegroundColor Yellow
    } else {
        # Check for uncommitted changes
        $gitStatus = git status --porcelain
        if ($gitStatus) {
            Write-Host "  Staging changes..." -ForegroundColor Cyan
            git add .
            
            # Generate commit message if not provided
            if (-not $CommitMessage) {
                $CommitMessage = "Deploy version $newVersion - Build $buildTimestamp"
            }
            
            Write-Host "  Committing changes..." -ForegroundColor Cyan
            git commit -m $CommitMessage
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  Commit failed (may be no changes)" -ForegroundColor Yellow
            } else {
                Write-Host "  Committed changes" -ForegroundColor Green
            }
        } else {
            Write-Host "  No changes to commit" -ForegroundColor Yellow
        }
        
        # Push to GitHub
        Write-Host "  Pushing to GitHub..." -ForegroundColor Cyan
        git push
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Push failed. Check your git remote and credentials." -ForegroundColor Yellow
            Write-Host "  You may need to run: git push manually" -ForegroundColor Yellow
        } else {
            Write-Host "  Pushed to GitHub" -ForegroundColor Green
        }
    }
    Write-Host ""
} else {
    Write-Host "Step 2: Skipping Git operations (SkipGit flag)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 3: Deploy
if (-not $SkipDeploy) {
    Write-Host "Step 3: Deploying to Firebase..." -ForegroundColor Yellow
    
    # Check Firebase CLI
    try {
        $firebaseVersion = firebase --version 2>&1
        Write-Host "  Firebase CLI: $firebaseVersion" -ForegroundColor Cyan
    } catch {
        Write-Host "  ERROR: Firebase CLI not found!" -ForegroundColor Red
        Write-Host "  Install with: npm install -g firebase-tools" -ForegroundColor Yellow
        exit 1
    }
    
    # Deploy hosting
    Write-Host "  Deploying hosting..." -ForegroundColor Cyan
    firebase deploy --only hosting
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Hosting deployment failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  Hosting deployed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Step 3: Skipping deployment (SkipDeploy flag)" -ForegroundColor Yellow
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Version: $currentVersion -> $newVersion" -ForegroundColor Cyan
Write-Host "Build: $buildTimestamp" -ForegroundColor Cyan
Write-Host "Date: $buildDate" -ForegroundColor Cyan
Write-Host ""
Write-Host "Site URL: https://hv-ecg.web.app" -ForegroundColor Cyan
Write-Host "Gallery: https://hv-ecg.web.app/gallery.html" -ForegroundColor Cyan
Write-Host ""
